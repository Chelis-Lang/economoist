module Economoist.Beacon_properties.Gordon_box
import Economoist.Growth (gordon_pv)
-- The division is well defined throughout this parameter box: r-g >= 0.04.
-- Beacon bounds this imported expression over real arithmetic, without a
-- claim about rounded f32 values.
@property gordon_pv_box_lower forall(d: f32, r: f32, g: f32) where d >= 0.5f32, d <= 1.0f32, r >= 0.08f32, r <= 0.1f32, g >= 0.02f32, g <= 0.04f32:
  (gordon_pv(d, r, g) >= 6.0f32)
@property gordon_pv_box_upper forall(d: f32, r: f32, g: f32) where d >= 0.5f32, d <= 1.0f32, r >= 0.08f32, r <= 0.1f32, g >= 0.02f32, g <= 0.04f32:
  (gordon_pv(d, r, g) <= 26.0f32)
@property gordon_pv_box_lower_wrong forall(d: f32, r: f32, g: f32) where d >= 0.5f32, d <= 1.0f32, r >= 0.08f32, r <= 0.1f32, g >= 0.02f32, g <= 0.04f32:
  (gordon_pv(d, r, g) >= 7.0f32)
@property gordon_pv_box_upper_wrong forall(d: f32, r: f32, g: f32) where d >= 0.5f32, d <= 1.0f32, r >= 0.08f32, r <= 0.1f32, g >= 0.02f32, g <= 0.04f32:
  (gordon_pv(d, r, g) <= 24.0f32)
