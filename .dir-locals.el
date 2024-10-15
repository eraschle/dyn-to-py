(
 (python-mode . ((eval . (dap-register-debug-template
                          "Python :: DynPy"
                          (list :name "Python :: Run DynPy"
                                :type "python"
                                :args ""
                                :cwd "${workspaceFolder}"
                                :module "dynpy"
                                :program nil
                                :request "launch"))))
              )
 )
