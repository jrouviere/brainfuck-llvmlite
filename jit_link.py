from ctypes import CFUNCTYPE, c_double

# from https://llvmlite.readthedocs.io/en/latest/user-guide/binding/examples.html

import llvmlite.binding as llvm

llvm.initialize()
llvm.initialize_native_target()
llvm.initialize_native_asmprinter()

def create_execution_engine():
    target = llvm.Target.from_default_triple()
    target_machine = target.create_target_machine()
    backing_mod = llvm.parse_assembly("")
    engine = llvm.create_mcjit_compiler(backing_mod, target_machine)
    return engine


def compile_ir(engine, llvm_ir, opt_level, dump_ir):
    mod = llvm.parse_assembly(llvm_ir)
    mod.verify()

    if dump_ir:
        print('---------- Initial LLVM IR ---------------')
        print(llvm_ir)


    # Optimize the module
    pmb = llvm.create_pass_manager_builder()
    pmb.opt_level = opt_level
    pm = llvm.create_module_pass_manager()
    pmb.populate(pm)
    pm.run(mod)

    if dump_ir:
        print('---------- Optimized LLVM IR ---------------')
        print(str(mod))

    engine.add_module(mod)
    engine.finalize_object()
    engine.run_static_constructors()
    return mod

def run(llvm_ir, opt_level=2, dump_ir=False):
    engine = create_execution_engine()
    mod = compile_ir(engine, llvm_ir, opt_level, dump_ir)
    
    func_ptr = engine.get_function_address("bfrun")

    # Run the function via ctypes
    cfunc = CFUNCTYPE(None)(func_ptr)
    cfunc()