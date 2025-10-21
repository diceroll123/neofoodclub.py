use chrono::DateTime;
use chrono_tz::Tz;
use pyo3::{exceptions::PyValueError, prelude::*, types::PyType};

use crate::{
    arena::{Arena, Arenas},
    bets::Bets,
    modifier::Modifier,
    odds_change::OddsChange,
    pirates::Pirate,
};

#[pyclass]
pub struct NeoFoodClub {
    pub inner: neofoodclub::nfc::NeoFoodClub,
}

unsafe impl Sync for NeoFoodClub {}

fn convert_probability_model_int_to_enum(
    probability_model: Option<u8>,
) -> PyResult<Option<neofoodclub::nfc::ProbabilityModel>> {
    match probability_model {
        Some(0) => Ok(Some(neofoodclub::nfc::ProbabilityModel::OriginalModel)),
        Some(1) => Ok(Some(
            neofoodclub::nfc::ProbabilityModel::MultinomialLogitModel,
        )),
        None => Ok(None),
        Some(v) => Err(PyValueError::new_err(format!(
            "Invalid probability model: {}. Must be 0 (OriginalModel), 1 (MultinomialLogitModel), or None.",
            v
        ))),
    }
}

#[pymethods]
impl NeoFoodClub {
    #[new]
    #[pyo3(signature = (json, bet_amount=None, probability_model=None, modifier=None))]
    fn new(
        json: &str,
        bet_amount: Option<u32>,
        probability_model: Option<u8>,
        modifier: Option<Modifier>,
    ) -> PyResult<Self> {
        Ok(NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_json(
                json,
                bet_amount,
                convert_probability_model_int_to_enum(probability_model)?,
                modifier.map(|m| m.inner),
            ),
        })
    }

    #[classmethod]
    #[pyo3(signature = (json, bet_amount=None, probability_model=None, modifier=None))]
    fn from_json(
        _cls: &Bound<'_, PyType>,
        json: &str,
        bet_amount: Option<u32>,
        probability_model: Option<u8>,
        modifier: Option<Modifier>,
    ) -> PyResult<Self> {
        Ok(NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_json(
                json,
                bet_amount,
                convert_probability_model_int_to_enum(probability_model)?,
                modifier.map(|m| m.inner),
            ),
        })
    }

    #[classmethod]
    #[pyo3(signature = (url, bet_amount=None, probability_model=None, modifier=None))]
    fn from_url(
        _cls: &Bound<'_, PyType>,
        url: &str,
        bet_amount: Option<u32>,
        probability_model: Option<u8>,
        modifier: Option<Modifier>,
    ) -> PyResult<Self> {
        Ok(NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_url(
                url,
                bet_amount,
                convert_probability_model_int_to_enum(probability_model)?,
                modifier.map(|m| m.inner),
            ),
        })
    }

    #[getter]
    fn modifier(&self) -> Modifier {
        Modifier::from(self.inner.modifier.clone())
    }

    #[pyo3(signature = (*, probability_model=None, modifier=None))]
    fn copy(&self, probability_model: Option<u8>, modifier: Option<Modifier>) -> PyResult<Self> {
        Ok(NeoFoodClub {
            inner: self.inner.copy(
                convert_probability_model_int_to_enum(probability_model)?,
                modifier.map(|m| m.inner),
            ),
        })
    }

    #[getter]
    fn arenas(&self) -> Arenas {
        let elements = self.inner.get_arenas().clone();
        Arenas::from(elements)
    }

    fn get_arena(&self, index: usize) -> PyResult<Arena> {
        let arena = self
            .inner
            .get_arenas()
            .get_arena(index)
            .ok_or_else(|| PyValueError::new_err(format!("Invalid arena index: {}", index)))?
            .clone();
        Ok(Arena::from(arena))
    }

    #[getter(bet_amount)]
    fn get_bet_amount(&self) -> Option<u32> {
        self.inner.bet_amount
    }

    #[setter(bet_amount)]
    fn set_bet_amount(&mut self, bet_amount: Option<u32>) {
        self.inner.set_bet_amount(bet_amount);
    }

    #[getter]
    fn winners<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, pyo3::types::PyTuple>> {
        pyo3::types::PyTuple::new(py, self.inner.winners())
    }

    #[getter]
    fn winners_binary(&self) -> u32 {
        self.inner.winners_binary()
    }

    #[getter]
    fn is_over(&self) -> bool {
        self.inner.is_over()
    }

    #[getter]
    fn round(&self) -> u16 {
        self.inner.round()
    }

    #[getter]
    fn start(&self) -> Option<String> {
        self.inner.start().to_owned()
    }

    #[getter]
    fn start_nst(&self) -> Option<DateTime<Tz>> {
        self.inner.start_nst()
    }

    #[getter]
    fn current_odds(&self) -> Vec<Vec<u8>> {
        self.inner
            .current_odds()
            .iter()
            .map(|o| o.to_vec())
            .collect()
    }

    #[getter]
    fn custom_odds(&self) -> Vec<Vec<u8>> {
        self.inner
            .custom_odds()
            .into_iter()
            .map(|o| o.to_vec())
            .collect()
    }

    #[getter]
    fn opening_odds(&self) -> Vec<Vec<u8>> {
        self.inner
            .opening_odds()
            .into_iter()
            .map(|o| o.to_vec())
            .collect()
    }

    #[getter]
    fn pirates(&self) -> Vec<Vec<u8>> {
        self.inner
            .pirates()
            .into_iter()
            .map(|o| o.to_vec())
            .collect()
    }

    #[getter]
    fn timestamp(&self) -> Option<DateTime<Tz>> {
        self.inner.timestamp_nst()
    }

    #[getter]
    fn last_change(&self) -> Option<DateTime<Tz>> {
        self.inner.last_change_nst()
    }

    #[getter]
    fn modified(&self) -> bool {
        self.inner.modified()
    }

    fn with_modifier(&mut self, modifier: Modifier) {
        self.inner.with_modifier(modifier.inner);
    }

    fn max_ters(&self) -> Vec<f64> {
        self.inner.max_ters().clone()
    }

    #[getter]
    fn foods(&self) -> Option<Vec<Vec<u8>>> {
        self.inner
            .foods()
            .map(|f| f.into_iter().map(|f| f.to_vec()).collect())
    }

    #[getter]
    fn changes(&self) -> Vec<OddsChange> {
        match self.inner.changes() {
            Some(changes) => changes
                .iter()
                .map(|c| OddsChange::from(c.clone()))
                .collect(),
            None => Vec::new(),
        }
    }

    #[getter]
    fn max_amount_of_bets(&self) -> usize {
        self.inner.max_amount_of_bets()
    }

    #[getter]
    fn get_winning_pirates(&self) -> Option<Vec<Pirate>> {
        self.inner
            .winning_pirates()
            .map(|pirates| pirates.into_iter().map(Pirate::from).collect::<Vec<_>>())
    }

    fn make_random_bets(&self) -> Bets {
        Bets::from(self.inner.make_random_bets())
    }

    fn make_tenbet_bets(&self, pirates_binary: u32) -> PyResult<Bets> {
        self.inner
            .make_tenbet_bets(pirates_binary)
            .map(Bets::from)
            .map_err(PyValueError::new_err)
    }

    fn make_max_ter_bets(&self) -> Bets {
        Bets::from(self.inner.make_max_ter_bets())
    }

    fn make_units_bets(&self, units: u32) -> Option<Bets> {
        self.inner.make_units_bets(units).map(Bets::from)
    }

    fn make_gambit_bets(&self, pirates_binary: u32) -> Bets {
        Bets::from(self.inner.make_gambit_bets(pirates_binary))
    }

    fn make_best_gambit_bets(&self) -> Bets {
        Bets::from(self.inner.make_best_gambit_bets())
    }

    fn make_winning_gambit_bets(&self) -> Option<Bets> {
        self.inner.make_winning_gambit_bets().map(Bets::from)
    }

    fn make_random_gambit_bets(&self) -> Bets {
        Bets::from(self.inner.make_random_gambit_bets())
    }

    fn make_crazy_bets(&self) -> Bets {
        Bets::from(self.inner.make_crazy_bets())
    }

    fn make_bustproof_bets(&self) -> Option<Bets> {
        self.inner.make_bustproof_bets().map(Bets::from)
    }

    fn make_bets_from_hash(&self, bets_hash: &str) -> PyResult<Bets> {
        self.inner
            .make_bets_from_hash(bets_hash)
            .map(Bets::from)
            .map_err(PyValueError::new_err)
    }

    fn make_bets_from_binaries(&self, binaries: Vec<u32>) -> Bets {
        Bets::from(self.inner.make_bets_from_binaries(binaries))
    }

    fn make_bets_from_indices(&self, indices: Vec<[u8; 5]>) -> Bets {
        Bets::from(self.inner.make_bets_from_indices(indices))
    }

    fn make_bets_from_array_indices(&self, indices: Vec<usize>) -> Bets {
        Bets::from(self.inner.make_bets_from_array_indices(indices))
    }

    fn get_win_units(&self, bets: &Bets) -> u32 {
        self.inner.get_win_units(&bets.inner)
    }

    fn get_win_np(&self, bets: &Bets) -> u32 {
        self.inner.get_win_np(&bets.inner)
    }

    fn __repr__(&self) -> String {
        format!(
            "<NeoFoodClub round={:?} bet_amount={:?}>",
            self.inner.round(),
            self.inner.bet_amount
        )
    }

    #[pyo3(signature = (*, bets=None, include_domain=true, all_data=false))]
    fn make_url(&self, bets: Option<&Bets>, include_domain: bool, all_data: bool) -> String {
        self.inner
            .make_url(bets.map(|b| &b.inner), include_domain, all_data)
    }

    #[getter]
    fn is_outdated_lock(&self) -> bool {
        self.inner.is_outdated_lock()
    }

    fn to_json(&self) -> String {
        self.inner.to_json()
    }
}
