;; Eval Buffer with `M-x eval-buffer' to register the newly created template.

(dap-register-debug-template
 "Python :: DynPy"
 (list :type "python"
       :args ""
       :cwd nil
       :env '(("DEBUG" . "1"))
       :module "app.py"
       :request "launch"
       :name "Python :: Run DynPy"))
