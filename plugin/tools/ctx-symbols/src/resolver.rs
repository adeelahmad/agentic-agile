// resolver.rs — symbol resolution backed by AstParser (harvested from ctxconfig src/plan/resolver.rs).

use std::fs;
use std::path::{Path, PathBuf};

use anyhow::{Context, Result};

use crate::ast::AstParser;

/// Structured resolution outcome.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Resolution {
    Found { start: usize, end: usize },
    FileMissing { path: PathBuf },
    SymbolMissingFromFile { path: PathBuf, symbol: String },
    LanguageUnsupported { path: PathBuf, extension: String },
}

/// Resolve a symbol with a detailed outcome enum.
pub fn resolve_symbol_detailed(
    parser: &mut AstParser,
    file: &Path,
    symbol: &str,
) -> Result<Resolution> {
    let extension = file
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_owned();

    if parser.get_language(&extension).is_none() {
        return Ok(Resolution::LanguageUnsupported {
            path: file.to_path_buf(),
            extension,
        });
    }

    if !file.exists() {
        return Ok(Resolution::FileMissing {
            path: file.to_path_buf(),
        });
    }

    let source = fs::read_to_string(file).with_context(|| format!("reading {}", file.display()))?;

    match parser.locate_symbol(&source, &extension, symbol)? {
        Some((start, end)) => Ok(Resolution::Found { start, end }),
        None => Ok(Resolution::SymbolMissingFromFile {
            path: file.to_path_buf(),
            symbol: symbol.to_owned(),
        }),
    }
}

/// Resolve a symbol in a file (collapsed Option form).
pub fn resolve_symbol(
    parser: &mut AstParser,
    file: &Path,
    symbol: &str,
) -> Result<Option<(usize, usize)>> {
    match resolve_symbol_detailed(parser, file, symbol)? {
        Resolution::Found { start, end } => Ok(Some((start, end))),
        _ => Ok(None),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Write;
    use tempfile::NamedTempFile;

    fn write_temp(ext: &str, body: &str) -> NamedTempFile {
        let f = tempfile::Builder::new()
            .suffix(&format!(".{ext}"))
            .tempfile()
            .unwrap();
        let mut handle = f.reopen().unwrap();
        handle.write_all(body.as_bytes()).unwrap();
        f
    }

    #[test]
    fn rust_struct_located() {
        let mut parser = AstParser::new().unwrap();
        let f = write_temp("rs", "pub struct Foo { pub a: i32 }\n");
        let r = resolve_symbol_detailed(&mut parser, f.path(), "Foo").unwrap();
        assert!(matches!(r, Resolution::Found { .. }));
    }

    #[test]
    fn missing_symbol_reported() {
        let mut parser = AstParser::new().unwrap();
        let f = write_temp("rs", "pub struct Other {}\n");
        let r = resolve_symbol_detailed(&mut parser, f.path(), "Foo").unwrap();
        assert!(matches!(r, Resolution::SymbolMissingFromFile { .. }));
    }

    #[test]
    fn unsupported_language_reported() {
        let mut parser = AstParser::new().unwrap();
        let r = resolve_symbol_detailed(&mut parser, Path::new("x.rb"), "Foo").unwrap();
        assert!(matches!(r, Resolution::LanguageUnsupported { .. }));
    }
}
