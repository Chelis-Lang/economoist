# Draft: resolve module imports in eval for standalone files

**Summary.** `prove` resolves module imports, so a property targets the real
exported shell function. `eval` on a standalone file does not resolve a package
import, so a one-line expression that calls an exported shell function cannot be
evaluated outside the package context.

**Impact on downstream shells.** A C Note template that wants the numeric value of
a shell model (for display alongside the proven property) must inline the model's
single-expression body, because it cannot `eval` a call to the exported function.
The proof surface is unaffected (prove resolves imports), so this is a numeric-
display ergonomics gap, not a soundness gap.

**Reproducer.** Write a standalone file that imports an exported package function
and evaluates a call to it; observe that the import does not resolve under
`eval`.

**Ask.** Resolve package imports in eval for standalone files, or provide an eval
mode that loads a package context and evaluates an inline expression against it.

**Filing condition.** eval still does not resolve standalone-file imports when a C
Note template needs it.
