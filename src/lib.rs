pub mod arena;
pub mod bets;
pub mod chance;
pub mod math;
pub mod modifier;
pub mod nfc;
pub mod odds;
pub mod pirates;

use neofoodclub;
use numpy::{ndarray::Array1, PyArray1, ToPyArray};
use pyo3::prelude::*;

#[pyfunction]
fn make_probabilities(opening_odds: Vec<Vec<u32>>) -> Vec<Vec<f64>> {
    let mut std: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    let mut min: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    let mut max: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    // let mut used: [[f64; 5]; 5] = [[1.0, 0.0, 0.0, 0.0, 0.0]; 5];
    // turns out we only use _std values in the python implementation of NFC
    // keeping the _used math to avoid confusion between NFC impls
    // however, if we use this Rust code on the frontend of neofood.club
    // that's the best time to expose this.

    for arena in 0..5 {
        let mut min_prob: f64 = 0.0;
        let mut max_prob: f64 = 0.0;

        for pirate in 1..5 {
            let pirate_odd: u32 = opening_odds[arena][pirate];
            if pirate_odd == 13 {
                min[arena][pirate] = 0.0;
                max[arena][pirate] = 1.0 / 13.0;
            } else if pirate_odd == 2 {
                min[arena][pirate] = 1.0 / 3.0;
                max[arena][pirate] = 1.0;
            } else {
                let p_o: f64 = pirate_odd as f64;
                min[arena][pirate] = 1.0 / (1.0 + p_o);
                max[arena][pirate] = 1.0 / p_o;
            }

            min_prob += min[arena][pirate];
            max_prob += max[arena][pirate];
        }

        for pirate in 1..5 {
            let min_original: f64 = min[arena][pirate];
            let max_original: f64 = max[arena][pirate];

            min[arena][pirate] = f64::max(min_original, 1.0 + max_original - max_prob);
            max[arena][pirate] = f64::min(max_original, 1.0 + min_original - min_prob);
            std[arena][pirate] = match opening_odds[arena][pirate] {
                13 => 0.05,
                _ => (min[arena][pirate] + max[arena][pirate]) / 2.0,
            };
        }

        for rectify_level in 2..13 {
            let mut rectify_count: f64 = 0.0;
            let mut std_total: f64 = 0.0;
            let mut rectify_value: f64 = 0.0;
            let mut max_rectify_value: f64 = 1.0;

            for pirate in 1..5 {
                std_total += std[arena][pirate];
                if opening_odds[arena][pirate] <= rectify_level {
                    rectify_count += 1.0;
                    rectify_value += std[arena][pirate] - min[arena][pirate];
                    max_rectify_value =
                        f64::min(max_rectify_value, max[arena][pirate] - min[arena][pirate]);
                }
            }

            if std_total == 1.0 {
                break;
            }

            if !(std_total - rectify_value > 1.0
                || rectify_count == 0.0
                || max_rectify_value * rectify_count < rectify_value + 1.0 - std_total)
            {
                rectify_value += 1.0 - std_total;
                rectify_value /= rectify_count;
                for pirate in 1..5 {
                    if opening_odds[arena][pirate] <= rectify_level {
                        std[arena][pirate] = min[arena][pirate] + rectify_value;
                    }
                }
                break;
            }
        }

        // let mut return_sum = 0.0;
        // for pirate in 1..5 {
        //     used[arena][pirate] = std[arena][pirate];
        //     return_sum += used[arena][pirate];
        // }

        // for pirate in 1..5 {
        //     used[arena][pirate] /= return_sum;
        // }
    }

    // convert std to a vector of vectors before returning
    std.iter().map(|&e| e.to_vec()).collect()
}

#[pyfunction]
fn make_round_dicts<'py>(
    py: Python<'py>,
    stds: [[f64; 5]; 5],
    odds: [[u8; 5]; 5],
) -> (
    &PyArray1<u32>,
    &PyArray1<f64>,
    &PyArray1<u32>,
    &PyArray1<f64>,
    &PyArray1<u32>,
) {
    let dicts = neofoodclub::math::make_round_dicts(stds, odds);

    (
        Array1::from_vec(dicts.bins).to_pyarray(py),
        Array1::from_vec(dicts.probs).to_pyarray(py),
        Array1::from_vec(dicts.odds).to_pyarray(py),
        Array1::from_vec(dicts.ers).to_pyarray(py),
        Array1::from_vec(dicts.maxbets).to_pyarray(py),
    )
}

#[pymodule]
#[pyo3(name = "neofoodclub")]
fn neofoodclub_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<math::Math>()?;
    m.add_class::<modifier::Modifier>()?;
    m.add_class::<nfc::NeoFoodClub>()?;
    m.add_class::<pirates::PartialPirate>()?;
    m.add_class::<pirates::Pirate>()?;
    m.add_function(wrap_pyfunction!(make_probabilities, m)?)?;
    m.add_function(wrap_pyfunction!(make_round_dicts, m)?)?;
    Ok(())
}
