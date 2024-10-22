(
 (python-mode . ((eval . (dap-register-debug-template
                          "DynPy >> APP"
                          (list :name "DynPy >> APP"
                                :type "python"
                                :args ""
                                :cwd "${workspaceFolder}"
                                :module "app"
                                :program nil
                                :request "launch")))
                 (eval . (dap-register-debug-template
                          "DynPy >> CLI"
                          (list :name "DynPy >> CLI"
                                :type "python"
                                :args '("--config" "CONFIG" "--source" "SOURCE" "--do-import")
                                :cwd "${workspaceFolder}"
                                :module "cli"
                                :program nil
                                :request "launch"))))))
