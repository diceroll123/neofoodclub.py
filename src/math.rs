use std::collections::HashMap;

use pyo3::prelude::*;

use crate::chance::Chance;

#[pyclass(name = "Math", module = "math", frozen)]
pub struct Math;

#[pymethods]
impl Math {
    #[classattr]
    const BIT_MASKS: [u32; 5] = neofoodclub::math::BIT_MASKS;

    #[classattr]
    pub const BET_AMOUNT_MIN: u32 = neofoodclub::math::BET_AMOUNT_MIN;

    #[classattr]
    pub const BET_AMOUNT_MAX: u32 = neofoodclub::math::BET_AMOUNT_MAX;

    #[staticmethod]
    fn pirate_binary(index: u8, arena: u8) -> u32 {
        neofoodclub::math::pirate_binary(index, arena)
    }

    #[staticmethod]
    fn pirates_binary(bets_indices: [u8; 5]) -> u32 {
        neofoodclub::math::pirates_binary(bets_indices)
    }

    #[staticmethod]
    fn binary_to_indices(binary: u32) -> (u8, u8, u8, u8, u8) {
        let arr = neofoodclub::math::binary_to_indices(binary);
        (arr[0], arr[1], arr[2], arr[3], arr[4])
    }

    #[staticmethod]
    fn bets_hash_to_bet_indices(bets_hash: &str) -> Vec<[u8; 5]> {
        neofoodclub::math::bets_hash_to_bet_indices(bets_hash)
    }

    #[staticmethod]
    fn bet_amounts_to_amounts_hash(bet_amounts: Vec<Option<u32>>) -> String {
        neofoodclub::math::bet_amounts_to_amounts_hash(&bet_amounts)
    }

    #[staticmethod]
    fn bets_hash_value(bets_indices: Vec<[u8; 5]>) -> String {
        neofoodclub::math::bets_hash_value(bets_indices)
    }

    #[staticmethod]
    fn amounts_hash_to_bet_amounts<'py>(
        py: Python<'py>,
        amounts_hash: &str,
    ) -> PyResult<Bound<'py, pyo3::types::PyTuple>> {
        let amounts = neofoodclub::math::amounts_hash_to_bet_amounts(amounts_hash);
        pyo3::types::PyTuple::new(py, amounts)
    }

    #[staticmethod]
    fn bets_hash_to_bet_binaries(bets_hash: &str) -> Vec<u32> {
        neofoodclub::math::bets_hash_to_bet_binaries(bets_hash)
    }

    #[staticmethod]
    fn bets_hash_to_bets_count(bets_hash: &str) -> usize {
        neofoodclub::math::bets_hash_to_bets_count(bets_hash)
    }

    #[staticmethod]
    fn bets_indices_to_bet_binaries(bets_indices: Vec<[u8; 5]>) -> Vec<u32> {
        neofoodclub::math::bets_indices_to_bet_binaries(bets_indices)
    }

    #[staticmethod]
    fn build_chance_objects(
        bets: Vec<[u8; 5]>,
        bet_odds: Vec<u32>,
        probabilities: [[f64; 5]; 5],
    ) -> Vec<Chance> {
        neofoodclub::math::build_chance_objects(&bets, &bet_odds, probabilities)
            .into_iter()
            .map(Chance::from)
            .collect()
    }

    #[staticmethod]
    fn expand_ib_object(bets: Vec<[u8; 5]>, bet_odds: Vec<u32>) -> HashMap<u32, u32> {
        neofoodclub::math::expand_ib_object(&bets, &bet_odds)
    }
}
