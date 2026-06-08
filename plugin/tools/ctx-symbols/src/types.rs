// types.rs — the two types AstParser depends on (harvested from ctxconfig src/types.rs).

use std::path::PathBuf;

/// How much of a source file to emit when processing content.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum IncludeMode {
    /// Full source code with all details.
    Full,
    /// Minified — comments and blank lines stripped (used to normalize bodies for hashing).
    #[default]
    Minified,
    /// Stubbed — signatures only.
    Stubbed,
    /// AST structure only.
    AstOnly,
}

impl IncludeMode {
    pub fn as_str(&self) -> &'static str {
        match self {
            Self::Full => "full",
            Self::Minified => "minified",
            Self::Stubbed => "stubbed",
            Self::AstOnly => "ast",
        }
    }
}

/// One AST search hit.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SearchResult {
    pub path: PathBuf,
    pub node_type: String,
    pub node_name: String,
    pub line_start: usize,
    pub line_end: usize,
    pub snippet: String,
}
