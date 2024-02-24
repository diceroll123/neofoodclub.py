pub mod chance;
pub mod math;

use itertools::iproduct;
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
    stds: Vec<Vec<f64>>,
    odds: Vec<Vec<u32>>,
) -> (
    &PyArray1<u32>,
    &PyArray1<f64>,
    &PyArray1<u32>,
    &PyArray1<f64>,
    &PyArray1<u32>,
) {
    let mut _bins: Array1<u32> = Array1::zeros(3124);
    let mut _stds: Array1<f64> = Array1::zeros(3124);
    let mut _odds: Array1<u32> = Array1::zeros(3124);
    let mut _ers: Array1<f64> = Array1::zeros(3124);
    let mut _maxbets: Array1<u32> = Array1::zeros(3124);

    let mut arr_index = 0;

    // the first iteration is an empty bet, so we skip it with skip(1)
    for (a, b, c, d, e) in iproduct!(0..5, 0..5, 0..5, 0..5, 0..5).skip(1) {
        let mut total_bin: u32 = 0;
        let mut total_stds: f64 = 1.0;
        let mut total_odds: u32 = 1;

        let nums = vec![a, b, c, d, e];
        for (arena, index) in nums.iter().enumerate() {
            if *index == 0 {
                continue;
            }
            total_bin += 1 << (19 - (index - 1 + arena * 4));
            total_stds *= stds[arena][*index];
            total_odds *= odds[arena][*index];
        }

        _bins[arr_index] = total_bin;
        _stds[arr_index] = total_stds;
        _odds[arr_index] = total_odds;
        _ers[arr_index] = total_stds * total_odds as f64;
        _maxbets[arr_index] = (1_000_000.0 / total_odds as f64).ceil() as u32;

        arr_index += 1;
    }

    (
        _bins.to_pyarray(py),
        _stds.to_pyarray(py),
        _odds.to_pyarray(py),
        _ers.to_pyarray(py),
        _maxbets.to_pyarray(py),
    )
}

#[pymodule]
#[pyo3(name = "neofoodclub")]
fn neofoodclub_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<math::Math>()?;
    m.add_function(wrap_pyfunction!(make_probabilities, m)?)?;
    m.add_function(wrap_pyfunction!(make_round_dicts, m)?)?;
    Ok(())
}
