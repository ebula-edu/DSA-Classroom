import sys
import os
import json
import tempfile
import subprocess
import traceback
import threading
import time
from io import StringIO

RUNNER_TEMPLATE = "" # Kept for backward compatibility if needed

class ThreadRedirector:
    def __init__(self, original):
        self.original = original
        self.redirects = {}
        
    def write(self, data):
        try:
            tid = threading.get_ident()
            if tid in self.redirects:
                self.redirects[tid].write(data)
            elif self.original is not None:
                self.original.write(data)
        except Exception:
            pass
            
    def flush(self):
        try:
            tid = threading.get_ident()
            if tid in self.redirects:
                self.redirects[tid].flush()
            elif self.original is not None:
                self.original.flush()
        except Exception:
            pass

def serialize_val(val, memo=None):
    if memo is None:
        memo = {}
    val_id = id(val)
    if val_id in memo:
        return {"type": "ref", "id": val_id}
    
    # Primitives
    if isinstance(val, (int, float, str, bool)) or val is None:
        return {"type": "primitive", "value": val}
    
    # Collections
    if isinstance(val, (list, tuple, set)):
        memo[val_id] = True
        return {
            "type": "list" if isinstance(val, list) else ("tuple" if isinstance(val, tuple) else "set"),
            "id": val_id,
            "value": [serialize_val(x, memo) for x in val]
        }
    if isinstance(val, dict):
        memo[val_id] = True
        res = {}
        for k, v in val.items():
            if isinstance(k, (int, float, str, bool)) or k is None:
                res[str(k)] = serialize_val(v, memo)
        return {"type": "dict", "id": val_id, "value": res}
        
    # Custom Objects
    if hasattr(val, "__dict__"):
        memo[val_id] = True
        attrs = {}
        for k, v in val.__dict__.items():
            if not k.startswith("__"):
                attrs[k] = serialize_val(v, memo)
        return {
            "type": "object",
            "class": val.__class__.__name__,
            "id": val_id,
            "value": attrs
        }
    return {"type": "primitive", "value": str(val)}

class ExecutionEngine:
    def __init__(self):
        if not isinstance(sys.stdout, ThreadRedirector):
            sys.stdout = ThreadRedirector(sys.stdout)
        if not isinstance(sys.stderr, ThreadRedirector):
            sys.stderr = ThreadRedirector(sys.stderr)
        
    def run_code(self, code_content, timeout=5.0):
        timeline = []
        stdout_buffer = StringIO()
        
        # Compile user code
        try:
            compiled = compile(code_content, "<user_code>", "exec")
        except SyntaxError as e:
            return {
                "error": "SyntaxError",
                "timeline": [{"line": e.lineno or 1, "event": "exception", "locals": {}, "output": f"SyntaxError at line {e.lineno}: {e.msg}"}]
            }
        except Exception as e:
            return {
                "error": "CompileError",
                "timeline": [{"line": 1, "event": "exception", "locals": {}, "output": f"Compile Error: {str(e)}"}]
            }
            
        start_time = time.time()
        timeout_reached = [False]
        
        def trace_func(frame, event, arg):
            if time.time() - start_time > timeout:
                timeout_reached[0] = True
                raise TimeoutError("Execution timed out")
                
            filename = frame.f_code.co_filename
            if filename != "<user_code>":
                return trace_func
                
            if event in ("line", "exception", "return"):
                local_vars = {}
                for name, val in frame.f_locals.items():
                    if not name.startswith("__"):
                        if not hasattr(val, "__call__") and not isinstance(val, type) and not sys.modules.get(name) == val:
                            local_vars[name] = serialize_val(val)
                
                timeline.append({
                    "line": frame.f_lineno,
                    "event": event,
                    "locals": local_vars,
                    "output": stdout_buffer.getvalue()
                })
            return trace_func

        exec_err = None
        
        def thread_target():
            nonlocal exec_err
            tid = threading.get_ident()
            sys.stdout.redirects[tid] = stdout_buffer
            sys.stderr.redirects[tid] = stdout_buffer
            sys.settrace(trace_func)
            try:
                global_scope = {"__file__": "<user_code>", "__name__": "__main__"}
                exec(compiled, global_scope)
            except TimeoutError:
                exec_err = "TimeoutExpired"
            except Exception as e:
                exec_err = str(e)
                traceback.print_exc(file=stdout_buffer)
                tb = sys.exc_info()[2]
                err_line = 1
                while tb:
                    if tb.tb_frame.f_code.co_filename == "<user_code>":
                        err_line = tb.tb_lineno
                    tb = tb.tb_next
                timeline.append({
                    "line": err_line,
                    "event": "exception",
                    "locals": {},
                    "output": stdout_buffer.getvalue(),
                    "exception": exec_err
                })
            finally:
                sys.settrace(None)
                if tid in sys.stdout.redirects:
                    del sys.stdout.redirects[tid]
                if tid in sys.stderr.redirects:
                    del sys.stderr.redirects[tid]
                
        t = threading.Thread(target=thread_target)
        t.start()
        t.join(timeout + 0.5)
        
        if t.is_alive():
            return {
                "error": "TimeoutExpired",
                "timeline": [{"line": 1, "event": "exception", "locals": {}, "output": "Execution timed out! (Possible infinite loop detected)"}]
            }
            
        if timeout_reached[0] or exec_err == "TimeoutExpired":
            return {
                "error": "TimeoutExpired",
                "timeline": [{"line": 1, "event": "exception", "locals": {}, "output": "Execution timed out! (Possible infinite loop detected)"}]
            }
            
        return {"error": exec_err, "timeline": timeline}

if __name__ == "__main__":
    test_code = """
x = 10
y = 20
arr = [1, 2, 3]
print("Sum:", x + y)
for i in range(len(arr)):
    arr[i] *= 2
"""
    engine = ExecutionEngine()
    res = engine.run_code(test_code)
    print("Error:", res.get("error"))
    print("Timeline Steps:", len(res.get("timeline", [])))
    for step in res.get("timeline", []):
        print(f"L{step['line']}: locals={step['locals']}, output={repr(step['output'])}")
