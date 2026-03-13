
#  Cost Analysis and Savings Modeling  
## Economic Validation of Cloud Optimization Engine

---

## 1️. Experiment Overview

This project was validated using real infrastructure deployed via Terraform in a clean Google Cloud project.

Two controlled states were measured:

- **Phase A (Baseline)** – 1 running VM, 3 unattached disks, 2 reserved static IPs  
- **Phase B (Scaled)** – 1 running VM, 5 stopped VMs, 3 unattached disks, 2 reserved static IPs  

All costs shown below are taken from **Billing → Reports → Usage cost ($)**.
Subtotal is zero because trial credits covered expenses, but *usage cost reflects real infrastructure consumption*.
1 credit = 1 CAD in this project, but the cost analysis is based on actual GCP pricing benchmarks.
---

## 2️. Baseline State (March 5–12)

### Infrastructure

- 1 × e2-medium (RUNNING)
- 3 × unattached disks (200GB, 100GB, 50GB)
- 2 × reserved static IP
- 1 × stopped VM

### Usage Cost (7 days)

| SKU | Cost (CAD) |
|------|------------|
| Static IP Charge | 4.84 |
| Storage PD Capacity | 3.06 |
| Compute | ~0 |
| **Total** | **7.91** |

### Projection

Monthly ≈ 7.91 × 4 = **31.6 CAD**  
Annual ≈ 31.6 × 12 = **~379 CAD**  

---

## 3️. Scaled State (+4 Stopped VMs)

Additional stopped VMs each had 10GB boot disk.

### Updated Usage Cost

| SKU | Cost (CAD) |
|------|------------|
| Static IP Charge | 5.43 |
| Storage PD Capacity | 3.69 |
| E2 Instance Core (running VM) | 0.41 |
| E2 Instance RAM (running VM) | 0.22 |
| **Total** | **9.84** |

### Delta (1 day growth)

Increase from 7.91 → 9.84

Δ = **+1.93 CAD**

---

## 4️. Financial Projection After Scaling

Daily exposure ≈ 1.93 CAD increase trend

Projected monthly impact:

1.93 × 30 ≈ **57.9 CAD/month**

Projected annual impact:

57.9 × 12 ≈ **~695 CAD/year**

---

## 5️. Key Findings

### 🔴 Static IP Waste
Unused reserved IP addresses were the largest contributor to waste.

### 🟠 Storage Waste
Unattached disks and boot disks of stopped VMs continuously accumulate cost.

### 🔵 Compute Cost
Running compute becomes visible once free-tier coverage is exceeded.

---

## 6️. FinOps Insight

Stopped VMs do not generate CPU cost, but they:

- Continue accumulating disk storage cost
- Represent lifecycle mismanagement
- Increase financial exposure when scaled

This experiment confirms:

- Infrastructure scale directly impacts cost  
- Storage waste compounds silently  
- Static IP waste is often overlooked  
- Automated detection provides measurable financial value  

---

## 7️. Strategic Conclusion

Even a small demo project generated:

**~700 CAD/year** projected exposure when scaled.

Extrapolated across:

- Multiple environments
- Multiple teams
- Organization-wide deployments

The impact becomes significant.

Cloud Optimization Engine provides:

- Continuous detection  
- Automated reporting  
- Financial visibility  
- Governance enforcement foundation  

This validates both technical automation and economic reasoning in a real cloud environment.
