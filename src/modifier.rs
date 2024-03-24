use chrono::NaiveTime;
use neofoodclub::modifier::ModifierFlags;
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyclass]
#[derive(Clone)]
pub struct Modifier {
    pub inner: neofoodclub::modifier::Modifier,
}

impl From<neofoodclub::modifier::Modifier> for Modifier {
    fn from(modifier: neofoodclub::modifier::Modifier) -> Self {
        Modifier { inner: modifier }
    }
}

#[pymethods]
impl Modifier {
    #[classattr]
    const EMPTY: i32 = ModifierFlags::EMPTY.bits();

    #[classattr]
    const GENERAL: i32 = ModifierFlags::GENERAL.bits();

    #[classattr]
    const OPENING_ODDS: i32 = ModifierFlags::OPENING_ODDS.bits();

    #[classattr]
    const REVERSE: i32 = ModifierFlags::REVERSE.bits();

    #[classattr]
    const CHARITY_CORNER: i32 = ModifierFlags::CHARITY_CORNER.bits();

    #[classattr]
    const ALL_MODIFIERS: i32 = ModifierFlags::all().bits();

    #[new]
    #[pyo3(signature = (value=0, custom_odds=None, custom_time=None))]
    pub fn new(
        value: i32,
        custom_odds: Option<HashMap<u8, u8>>,
        custom_time: Option<String>,
    ) -> Self {
        Modifier {
            inner: neofoodclub::modifier::Modifier::new(
                value,
                custom_odds,
                custom_time.map(|s| NaiveTime::parse_from_str(&s, "%H:%M:%S").unwrap()),
            ),
        }
    }

    #[getter]
    fn value(&self) -> i32 {
        self.inner.value
    }

    #[getter]
    pub fn is_empty(&self) -> bool {
        self.inner.is_empty()
    }
    #[getter]
    pub fn is_general(&self) -> bool {
        self.inner.is_general()
    }
    #[getter]
    pub fn is_opening_odds(&self) -> bool {
        self.inner.is_opening_odds()
    }
    #[getter]
    pub fn is_reverse(&self) -> bool {
        self.inner.is_reverse()
    }
    #[getter]
    pub fn is_charity_corner(&self) -> bool {
        self.inner.is_charity_corner()
    }

    #[getter]
    pub fn custom_odds(&self) -> Option<HashMap<u8, u8>> {
        self.inner.custom_odds.clone()
    }

    #[getter]
    pub fn custom_time(&self) -> Option<String> {
        self.inner
            .custom_time
            .map(|t| t.format("%H:%M:%S").to_string())
    }

    pub fn __eq__(&self, other: &Modifier) -> bool {
        self.inner == other.inner
    }

    pub fn copy(&self) -> Self {
        Modifier {
            inner: self.inner.copy(),
        }
    }

    pub fn __repr__(&self) -> String {
        format!(
            "<Modifier value={:b} custom_odds={:?} custom_time={:?}>",
            self.inner.value, self.inner.custom_odds, self.inner.custom_time
        )
    }
}
