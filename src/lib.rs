pub mod arena;
pub mod bets;
pub mod chance;
pub mod math;
pub mod modifier;
pub mod nfc;
pub mod odds;
pub mod odds_change;
pub mod pirates;

use pyo3::prelude::*;

#[pymodule]
#[pyo3(name = "neofoodclub")]
fn neofoodclub_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<math::Math>()?;
    m.add_class::<modifier::Modifier>()?;
    m.add_class::<nfc::NeoFoodClub>()?;
    m.add_class::<bets::Bets>()?;
    m.add_class::<pirates::PartialPirate>()?;
    m.add_class::<pirates::Pirate>()?;
    Ok(())
}
