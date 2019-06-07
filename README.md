# README

This is a basic tool set to convert between the staff-based MEI format used in
[Neon](https://github.com/DDMAL/Neon2). It converts this to a file with a single
`<staff>` element and many `<sb>` elements. The `@facs` of `<sb>` elements
is the same as of the `<staff>` elements they replace.

Ideally this will be integrated into Neon eventually in some form and currently
exists to work out how to handle going between these two file types successfully.
