# Main formulas

## Discount factor
P(0, T)

## Continuous zero rate
z(T) = -log(P(0,T)) / T

## Forward discount factor
P(t, T) = P(0,T) / P(0,t)

## Extended rate
R_j(t) = ( P(t, T_{j-1}) / P(t, T_j) - 1 ) / tau_j

## FRN price
V_FRN(t) = N * sum_j tau_j * P(0, T_j) * (R_j(t) + s) + N * P(0, T_n)

## Payer swap value
V_swap(t) = float_leg - fixed_leg

float_leg = sum_j tau_j * P(0, T_j) * R_j(t)
fixed_leg = K * sum_j tau'_j * P(0, T'_j)

## Par swap rate
K_par = numerator / denominator
