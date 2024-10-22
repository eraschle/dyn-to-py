import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Optional

from dynpy.ui.convert.models import AFileViewModel, ANodeViewModel, ATreeViewModel
from dynpy.ui.convert.controller import ConvertController
from dynpy.ui.models.uiargs import UiArgs


class ModelListBox(tk.LabelFrame):
    def __init__(self, controller: ConvertController, text: str):
        super().__init__(text=text)
        args = UiArgs()
        self.controller = controller
        self._node_id_dict: Dict[str, ANodeViewModel] = {}
        self._model_id_dict: Dict[str, AFileViewModel] = {}
        self.grid_rowconfigure(**args.row_args(weight=0))
        self.grid_columnconfigure(**args.column_args())
        self.var_root_path = self.add_heading_frame(args)
        args.add_row()
        self.grid_rowconfigure(**args.row_args(weight=1))
        self.tree_files = ttk.Treeview(self)
        self.tree_files.bind("<<TreeviewSelect>>", self.controller.on_tree_select)
        self.tree_files.grid(cnf=args.grid_args(sticky=tk.NSEW))

    def add_heading_frame(self, args_frame: UiArgs) -> tk.StringVar:
        frm_root = tk.Frame(self)
        frm_root.grid(cnf=args_frame.grid_args(columnspan=2))
        args = args_frame.create(row=0, column=0, sticky=tk.NSEW)
        frm_root.grid_rowconfigure(**args.row_args(weight=0))
        frm_root.grid_columnconfigure(**args.column_args(weight=0, minsize=args.east_min))
        lbl_root = tk.Label(frm_root, text="Root-Path", anchor=tk.W)
        lbl_root.grid(cnf=args.grid_args(sticky=tk.W))
        args.add_column()
        frm_root.grid_columnconfigure(**args.column_args(weight=1))
        var_root_path = tk.StringVar(master=frm_root, value="")
        lbl_path = tk.Label(frm_root, textvariable=var_root_path, anchor=tk.W)
        lbl_path.grid(cnf=args.grid_args(sticky=tk.EW))
        return var_root_path

    @property
    def text(self) -> str:
        return self.cget("text")

    @text.setter
    def text(self, value: str):
        self.config(text=value)

    def selected_code_node(self) -> Optional[ANodeViewModel]:
        selected = self.tree_files.selection()
        if len(selected) != 1:
            return None
        return self._node_id_dict.get(selected[0], None)

    def selected_file_model(self) -> Optional[AFileViewModel]:
        selected = self.tree_files.selection()
        if len(selected) != 1:
            return None
        return self._model_id_dict.get(selected[0], None)

    def selected_other_view_models(self) -> List[ATreeViewModel]:
        model = self.selected_file_model()
        other = None if model is None else model.other_model
        if other is not None:
            return [other]
        model = self.selected_code_node()
        other = None if model is None else model.other_node
        if model is None or other is None:
            return []
        parent_id = self.tree_files.parent(model.tree_id)
        parent = self._model_id_dict.get(parent_id, None)
        parent = None if parent is None else parent.other_model
        return [mdl for mdl in (parent, other) if mdl is not None]

    def select_model(self, models: List[ATreeViewModel]):
        for idx, model in enumerate(models, start=1):
            self.tree_files.selection_set(model.tree_id)
            if idx == len(models):
                self.tree_files.see(model.tree_id)
            else:
                self.tree_files.item(model.tree_id, open=True)

    def clean_values(self):
        self.tree_files.delete(*self.tree_files.get_children())

    def add_children(self, view_model: AFileViewModel):
        for child in view_model.children:
            tree_id = self.tree_files.insert(
                view_model.tree_id,
                tk.END,
                text=child.name,
                tags=self.controller.node_tags_for(child),
            )
            child.tree_id = tree_id
            self._node_id_dict[tree_id] = child

    def add_models(self):
        for idx, view_model in enumerate(self.controller.view_models):
            if idx == 0:
                self.var_root_path.set(str(view_model.root))
            tree_id = self.tree_files.insert(
                "",
                tk.END,
                text=view_model.name,
                tags=self.controller.model_tags_for(view_model),
            )
            view_model.tree_id = tree_id
            self._model_id_dict[tree_id] = view_model
            self.add_children(view_model)

    def update_children_tags(self, view_model: AFileViewModel):
        for child in view_model.children:
            self.tree_files.item(child.tree_id, tags=self.controller.node_tags_for(child))

    def update_tags(self):
        for model in self.controller.view_models:
            self.tree_files.item(model.tree_id, tags=self.controller.model_tags_for(model))
            self.update_children_tags(model)

    def update_files(self):
        self.clean_values()
        self.add_models()
        self.update_tags()
