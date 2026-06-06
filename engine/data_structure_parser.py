import sys

class DataStructureParser:
    def __init__(self):
        pass
        
    def parse_state(self, local_vars):
        """
        Parses a dictionary of local variables (from execution_engine) 
        and groups them into structured data models.
        """
        # Flat object registry mapping: id -> serialized_object_dict
        # We need this to trace references
        object_map = {}
        
        # Helper to populate object_map recursively
        def build_object_map(val):
            if not isinstance(val, dict):
                return
            val_type = val.get("type")
            if val_type == "object":
                obj_id = val.get("id")
                if obj_id not in object_map:
                    object_map[obj_id] = val
                    for attr_val in val.get("value", {}).values():
                        build_object_map(attr_val)
            elif val_type in ("list", "tuple", "set"):
                for item in val.get("value", []):
                    build_object_map(item)
            elif val_type == "dict":
                for item in val.get("value", {}).values():
                    build_object_map(item)

        # Build the object map from all variables
        for name, val in local_vars.items():
            build_object_map(val)
            
        parsed = {
            "primitives": {},      # name -> value_str
            "arrays": {},          # name -> [elements]
            "stacks": {},          # name -> [elements]
            "queues": {},          # name -> [elements]
            "dicts": {},           # name -> {key: value}
            "linked_lists": {},    # name -> {"head_id": id, "nodes": {id: {val, next_id}}}
            "trees": {},           # name -> {"root_id": id, "nodes": {id: {val, left_id, right_id}}}
            "graphs": {},          # name -> {"nodes": [], "edges": []}
            "pointers": {}         # name -> target_object_id (for nodes/objects)
        }
        
        # Helper to resolve references
        def resolve(val):
            if not isinstance(val, dict):
                return val
            if val.get("type") == "ref":
                ref_id = val.get("id")
                return object_map.get(ref_id, val)
            return val

        def get_primitive_val(val):
            val = resolve(val)
            if val.get("type") == "primitive":
                return val.get("value")
            elif val.get("type") == "ref":
                return f"Ref({val.get('id')})"
            elif val.get("type") == "object":
                # Find an attribute like 'val', 'value', 'data'
                attrs = val.get("value", {})
                for k in ("val", "value", "data", "item"):
                    if k in attrs:
                        r = resolve(attrs[k])
                        if r.get("type") == "primitive":
                            return r.get("value")
                return f"{val.get('class')}()"
            return str(val)

        # We keep track of object ids that are part of structures (linked lists, trees)
        # to distinguish them from standard pointer variables
        structured_node_ids = set()

        # 1. Identify Trees and Linked Lists first
        # We look for variables pointing to custom objects containing standard fields
        for name, var_val in local_vars.items():
            resolved_val = resolve(var_val)
            if not resolved_val or resolved_val.get("type") != "object":
                continue
                
            attrs = resolved_val.get("value", {})
            
            # Check for binary tree (left/right children)
            is_tree = any(k in attrs for k in ("left", "right", "left_child", "right_child"))
            # Check for linked list node (next)
            is_ll = any(k in attrs for k in ("next", "nxt", "next_node"))
            
            if is_tree:
                root_id = resolved_val.get("id")
                tree_nodes = {}
                visited = set()
                
                # Traverse tree
                def traverse_tree(node_id):
                    if not node_id or node_id in visited:
                        return
                    visited.add(node_id)
                    obj = object_map.get(node_id)
                    if not obj:
                        return
                    attrs = obj.get("value", {})
                    
                    # Extract val
                    val = "?"
                    for val_k in ("val", "value", "data", "key", "item"):
                        if val_k in attrs:
                            val = get_primitive_val(attrs[val_k])
                            break
                            
                    # Extract left & right
                    left_id = None
                    right_id = None
                    for l_k in ("left", "left_child"):
                        if l_k in attrs:
                            l_val = resolve(attrs[l_k])
                            if l_val and l_val.get("type") == "object":
                                left_id = l_val.get("id")
                    for r_k in ("right", "right_child"):
                        if r_k in attrs:
                            r_val = resolve(attrs[r_k])
                            if r_val and r_val.get("type") == "object":
                                right_id = r_val.get("id")
                                
                    tree_nodes[node_id] = {
                        "val": val,
                        "left_id": left_id,
                        "right_id": right_id
                    }
                    structured_node_ids.add(node_id)
                    if left_id:
                        traverse_tree(left_id)
                    if right_id:
                        traverse_tree(right_id)
                        
                traverse_tree(root_id)
                parsed["trees"][name] = {
                    "root_id": root_id,
                    "nodes": tree_nodes
                }
                
            elif is_ll:
                head_id = resolved_val.get("id")
                ll_nodes = {}
                visited = set()
                curr_id = head_id
                
                # Traverse linked list
                while curr_id and curr_id not in visited:
                    visited.add(curr_id)
                    obj = object_map.get(curr_id)
                    if not obj:
                        break
                    attrs = obj.get("value", {})
                    
                    # Extract value
                    val = "?"
                    for val_k in ("val", "value", "data", "item"):
                        if val_k in attrs:
                            val = get_primitive_val(attrs[val_k])
                            break
                            
                    # Extract next
                    next_id = None
                    for n_k in ("next", "nxt", "next_node"):
                        if n_k in attrs:
                            n_val = resolve(attrs[n_k])
                            if n_val and n_val.get("type") == "object":
                                next_id = n_val.get("id")
                            break
                            
                    ll_nodes[curr_id] = {
                        "val": val,
                        "next_id": next_id
                    }
                    structured_node_ids.add(curr_id)
                    curr_id = next_id
                    
                parsed["linked_lists"][name] = {
                    "head_id": head_id,
                    "nodes": ll_nodes
                }

        # 2. Process other variables (lists, dicts, primitives, pointers)
        for name, var_val in local_vars.items():
            resolved_val = resolve(var_val)
            val_type = resolved_val.get("type") if resolved_val else None
            
            if not val_type:
                continue
                
            # If it's a pointer to an already indexed tree/linked-list node
            if val_type == "object" and resolved_val.get("id") in structured_node_ids:
                parsed["pointers"][name] = resolved_val.get("id")
                continue
                
            if val_type == "list":
                elements = []
                for item in resolved_val.get("value", []):
                    elements.append(get_primitive_val(item))
                    
                # Naming-based heuristics for Stacks and Queues
                lower_name = name.lower()
                if "stack" in lower_name or lower_name == "s":
                    parsed["stacks"][name] = elements
                elif "queue" in lower_name or lower_name == "q":
                    parsed["queues"][name] = elements
                else:
                    parsed["arrays"][name] = elements
                    
            elif val_type == "dict":
                # Check if it represents a Graph (adjacency list: keys point to lists of values)
                is_graph = True
                nodes = []
                edges = []
                raw_dict = resolved_val.get("value", {})
                
                if not raw_dict:
                    is_graph = False
                else:
                    for k, v in raw_dict.items():
                        resolved_v = resolve(v)
                        if resolved_v.get("type") != "list":
                            is_graph = False
                            break
                        nodes.append(str(k))
                        for item in resolved_v.get("value", []):
                            dest = get_primitive_val(item)
                            edges.append((str(k), str(dest)))
                            
                if is_graph:
                    # Clean graph representation
                    all_nodes = set(nodes)
                    for u, v in edges:
                        all_nodes.add(v)
                    parsed["graphs"][name] = {
                        "nodes": list(all_nodes),
                        "edges": edges
                    }
                else:
                    # Render as standard dict
                    items = {}
                    for k, v in raw_dict.items():
                        items[str(k)] = get_primitive_val(v)
                    parsed["dicts"][name] = items
                    
            elif val_type == "primitive":
                parsed["primitives"][name] = resolved_val.get("value")
                
            elif val_type == "object":
                # It's an arbitrary object, print it as a primitive class name or dict
                attrs = {}
                for k, v in resolved_val.get("value", {}).items():
                    attrs[k] = get_primitive_val(v)
                parsed["dicts"][name] = {f"{resolved_val.get('class')}.{k}": v for k, v in attrs.items()}
                
        return parsed

# Quick test if run directly
if __name__ == "__main__":
    # Mock local vars
    mock_locals = {
        "x": {"type": "primitive", "value": 42},
        "arr": {"type": "list", "id": 1, "value": [
            {"type": "primitive", "value": 10},
            {"type": "primitive", "value": 20}
        ]},
        "stack_var": {"type": "list", "id": 2, "value": [
            {"type": "primitive", "value": 5}
        ]},
        "head": {"type": "object", "class": "Node", "id": 100, "value": {
            "val": {"type": "primitive", "value": "A"},
            "next": {"type": "ref", "id": 101}
        }},
        "curr": {"type": "ref", "id": 101},
        "g": {"type": "dict", "id": 3, "value": {
            "A": {"type": "list", "id": 4, "value": [{"type": "primitive", "value": "B"}]},
            "B": {"type": "list", "id": 5, "value": []}
        }}
    }
    
    # We need the referenced objects in the map
    mock_locals["head"]["value"]["next"] = {"type": "object", "class": "Node", "id": 101, "value": {
        "val": {"type": "primitive", "value": "B"},
        "next": {"type": "primitive", "value": None}
    }}
    
    parser = DataStructureParser()
    res = parser.parse_state(mock_locals)
    import pprint
    pprint.pprint(res)
