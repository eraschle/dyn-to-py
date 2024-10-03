Definitions = IN[0]  # pyright: ignore[reportUndefinedVariable]

Unique = []
Added = []

for elem in Definitions:
    if elem.Name in Added:
        continue
    Added.append(elem.Name)
    Unique.append(elem)

OUT = sorted(Unique, key=lambda ele: ele.Name)
