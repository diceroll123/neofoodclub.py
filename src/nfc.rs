use pyo3::{
    exceptions::PyValueError,
    prelude::*,
    types::{PyTuple, PyType},
};

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

fn convert_probability_model_int_to_enum(
    probability_model: Option<u8>,
) -> Option<neofoodclub::nfc::ProbabilityModel> {
    match probability_model {
        Some(0) => Some(neofoodclub::nfc::ProbabilityModel::OriginalModel),
        Some(1) => Some(neofoodclub::nfc::ProbabilityModel::MultinomialLogitModel),
        None => None,
        _ => panic!("Invalid probability model"),
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
    ) -> Self {
        NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_json(
                json,
                bet_amount,
                convert_probability_model_int_to_enum(probability_model),
                modifier.map(|m| m.inner),
            ),
        }
    }

    #[classmethod]
    #[pyo3(signature = (json, bet_amount=None, probability_model=None, modifier=None))]
    fn from_json(
        _cls: &PyType,
        json: &str,
        bet_amount: Option<u32>,
        probability_model: Option<u8>,
        modifier: Option<Modifier>,
    ) -> Self {
        NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_json(
                json,
                bet_amount,
                convert_probability_model_int_to_enum(probability_model),
                modifier.map(|m| m.inner),
            ),
        }
    }

    #[classmethod]
    #[pyo3(signature = (url, bet_amount=None, probability_model=None, modifier=None))]
    fn from_url(
        _cls: &PyType,
        url: &str,
        bet_amount: Option<u32>,
        probability_model: Option<u8>,
        modifier: Option<Modifier>,
    ) -> Self {
        NeoFoodClub {
            inner: neofoodclub::nfc::NeoFoodClub::from_url(
                url,
                bet_amount,
                convert_probability_model_int_to_enum(probability_model),
                modifier.map(|m| m.inner),
            ),
        }
    }

    #[getter]
    fn modifier(&self) -> Modifier {
        Modifier::from(self.inner.modifier.clone())
    }

    #[pyo3(signature = (*, probability_model=None, modifier=None))]
    fn copy(&self, probability_model: Option<u8>, modifier: Option<Modifier>) -> Self {
        NeoFoodClub {
            inner: self.inner.copy(
                convert_probability_model_int_to_enum(probability_model),
                modifier.map(|m| m.inner),
            ),
        }
    }

    #[getter]
    fn arenas(&self) -> Arenas {
        let elements = self.inner.get_arenas().clone();
        Arenas::from(elements)
    }

    fn get_arena(&self, index: usize) -> Arena {
        let arena = self
            .inner
            .get_arenas()
            .get_arena(index)
            .expect("Invalid index")
            .clone();
        Arena::from(arena)
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
    fn winners<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.winners();
        Ok(PyTuple::new(py, elements))
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
    fn start_nst(&self) -> Option<String> {
        self.inner.start_nst().map(|t| t.to_rfc3339())
    }

    #[getter]
    fn current_odds<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.current_odds();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn custom_odds<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.custom_odds();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn opening_odds<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.opening_odds();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn pirates<'a>(&self, py: Python<'a>) -> PyResult<&'a PyTuple> {
        let elements = self.inner.pirates();
        Ok(PyTuple::new(py, elements))
    }

    #[getter]
    fn timestamp(&self) -> Option<String> {
        self.inner.timestamp().to_owned()
    }

    #[getter]
    fn last_change(&self) -> Option<String> {
        self.inner.last_change().to_owned()
    }

    #[getter]
    fn modified(&self) -> bool {
        self.inner.modified()
    }

    fn with_modifier(&mut self, modifier: Modifier) {
        self.inner.with_modifier(modifier.inner.clone());
    }

    #[getter]
    fn foods<'a>(&self, py: Python<'a>) -> PyResult<Option<&'a PyTuple>> {
        let elements = self.inner.foods();

        match elements {
            Some(e) => Ok(Some(PyTuple::new(py, e))),
            None => Ok(None),
        }
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
            .map(|pirates| pirates.iter().map(|p| Pirate::from(**p)).collect())
    }

    fn make_random_bets(&self) -> Bets {
        Bets::from(self.inner.make_random_bets())
    }

    fn make_tenbet_bets(&self, pirates_binary: u32) -> PyResult<Bets> {
        let bets = self.inner.make_tenbet_bets(pirates_binary);

        match bets {
            Ok(bets) => Ok(Bets::from(bets)),
            Err(s) => Err(PyValueError::new_err(s)),
        }
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

    fn make_bets_from_hash(&self, bets_hash: &str) -> Bets {
        Bets::from(self.inner.make_bets_from_hash(bets_hash))
    }

    fn make_bets_from_binaries(&self, binaries: Vec<u32>) -> Bets {
        Bets::from(self.inner.make_bets_from_binaries(binaries))
    }

    fn make_bets_from_indices(&self, indices: Vec<[u8; 5]>) -> Bets {
        Bets::from(self.inner.make_bets_from_indices(indices))
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
