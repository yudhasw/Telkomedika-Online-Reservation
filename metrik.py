import ast
import os
from radon.complexity import cc_visit

def analyze_class(node, content):
    """Menganalisis satu node Class untuk metrik CK"""
    class_name = node.name
    methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
    
    # 1. WMC (Weighted Methods per Class)
    # Kita gunakan Sum of Cyclomatic Complexity dari Radon
    try:
        wmc = sum([m.complexity for m in cc_visit(content) if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))])
        # Filter hanya complexity milik class ini (agak tricky di AST flat, kita estimasi pakai jumlah method + branch sederhana)
        wmc = 0
        for m in methods:
            # Hitung branch sederhana manual untuk estimasi cepat WMC
            complexity = 1 
            for child in ast.walk(m):
                if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                    complexity += 1
            wmc += complexity
    except:
        wmc = len(methods) # Fallback: jumlah method

    # 2. DIT (Depth of Inheritance Tree)
    # Asumsi: Class db.Model dihitung level 1. Object biasa level 0.
    dit = 0
    if node.bases:
        dit = 1 # Punya parent
        # Cek jika parentnya juga class buatan kita (bukan db.Model) - simplifikasi
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id not in ['db.Model', 'object']:
                dit = 2 

    # 3. NOC (Number of Children)
    # (Dihitung di luar fungsi ini setelah semua class terkumpul)
    noc = 0 

    # 4. RFC (Response For a Class)
    # Jumlah method di class ini + jumlah pemanggilan fungsi eksternal di dalam class
    local_methods = {m.name for m in methods}
    called_functions = set()
    for m in methods:
        for child in ast.walk(m):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    called_functions.add(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    called_functions.add(child.func.attr)
    
    # RFC = Jumlah Method Sendiri + Jumlah Method Unik yang Dipanggil
    rfc = len(local_methods) + len(called_functions)

    # 5. CBO (Coupling Between Objects)
    # Dihitung dari Import + Atribut tipe data lain
    cbo = 0
    # Simplifikasi: Hitung berapa banyak tipe unik yang disebut di argumen fungsi
    unique_types = set()
    for m in methods:
        for arg in m.args.args:
            if arg.annotation:
                if isinstance(arg.annotation, ast.Name):
                    unique_types.add(arg.annotation.id)
    cbo = len(unique_types)
    # Tambah poin jika mewarisi sesuatu (Inheritance is coupling)
    if dit > 0: cbo += 1

    # 6. LCOM (Lack of Cohesion in Methods) - Versi Henderson-Sellers (LCOM*)
    # Menghitung irisan penggunaan atribut instance (self.x)
    instance_vars = set()
    method_access = {m.name: set() for m in methods}
    
    for m in methods:
        for child in ast.walk(m):
            if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == 'self':
                instance_vars.add(child.attr)
                method_access[m.name].add(child.attr)
    
    # Rumus LCOM Sederhana: (M - sum(P) / F) / (M-1) 
    # M = jumlah method, F = jumlah atribut, P = berapa method yg akses atribut X
    num_m = len(methods)
    num_f = len(instance_vars)
    
    lcom = 0.0
    if num_m > 1 and num_f > 0:
        sum_access = sum(len(v) for v in method_access.values())
        avg_access = sum_access / num_f
        lcom = (avg_access - num_m) / (1 - num_m)
        # Normalisasi ke 0-1 (mendekati 0 bagus, mendekati 1 buruk)
        lcom = abs(lcom) # LCOM kadang negatif di rumus lain, kita ambil magnitude
    
    return {
        "Class": class_name,
        "WMC": wmc,
        "DIT": dit,
        "NOC": noc, # Placeholder
        "CBO": cbo,
        "RFC": rfc,
        "LCOM": round(lcom, 2)
    }

def scan_files(folder_path):
    results = []
    class_parents = {} # Untuk hitung NOC: {Parent: [Anak1, Anak2]}

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        content = f.read()
                        tree = ast.parse(content)
                        for node in tree.body:
                            if isinstance(node, ast.ClassDef):
                                metrics = analyze_class(node, content)
                                results.append(metrics)
                                
                                # Catat Parent untuk NOC
                                for base in node.bases:
                                    if isinstance(base, ast.Name):
                                        p_name = base.id
                                        if p_name not in class_parents: class_parents[p_name] = []
                                        class_parents[p_name].append(node.name)
                    except Exception as e:
                        print(f"Skip {file}: {e}")

    # Update NOC values
    final_results = []
    for r in results:
        cls_name = r['Class']
        # Cek apakah class ini menjadi parent bagi class lain?
        if cls_name in class_parents:
            r['NOC'] = len(class_parents[cls_name])
        else:
            r['NOC'] = 0
        final_results.append(r)

    return final_results

if __name__ == "__main__":
    print(f"{'CLASS':<25} | {'WMC':<5} | {'DIT':<5} | {'NOC':<5} | {'CBO':<5} | {'RFC':<5} | {'LCOM':<5}")
    print("-" * 75)
    
    # GANTI 'models' DENGAN FOLDER YANG MAU DI CEK
    metrics_data = scan_files("models") 
    
    for m in metrics_data:
        print(f"{m['Class']:<25} | {m['WMC']:<5} | {m['DIT']:<5} | {m['NOC']:<5} | {m['CBO']:<5} | {m['RFC']:<5} | {m['LCOM']:<5}")