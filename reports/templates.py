"""
reports/templates.py
=====================
Text template builders for each section of the model summary report.
Each function returns a list of strings — joined with newlines by the generator.
"""

from datetime import datetime


def header(client: str) -> list:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return [
        "=" * 80,
        "MODEL PERFORMANCE REPORT",
        f"Client: {client}",
        f"Generated: {ts}",
        "=" * 80,
    ]


def executive_summary(winner_name: str, metrics: dict) -> list:
    lift   = metrics.get('Lift_Decile_1', 0)
    gains  = metrics.get('Gains_Decile_1', 0)
    auc    = metrics.get('AUC', 0)
    ks     = metrics.get('KS_Statistic', 0)
    misclass = metrics.get('Misclass_Rate', 0)

    return [
        "", "=" * 80, "1. EXECUTIVE SUMMARY", "=" * 80,
        f"\nWinning Model: {winner_name}",
        "\nKey Performance Metrics (Validation):",
        f"  - Lift at Top Decile:      {lift:.3f}",
        f"  - Gains at Top Decile:     {gains*100:.1f}%",
        f"  - AUC:                     {auc:.4f}",
        f"  - KS Statistic:            {ks:.4f}",
        f"  - Misclassification Rate:  {misclass*100:.2f}%",
        "\nInterpretation:",
        f"  - The model is {lift:.2f}x better than random in the top 10%",
        f"  - {gains*100:.1f}% of all responders are captured in the top 10% of scored records",
    ]


def model_comparison(comparison_df) -> list:
    lines = ["", "=" * 80, "2. MODEL COMPARISON", "=" * 80, ""]
    lines.append(f"{'Rank':<6} {'Model':<25} {'Lift D1':<12} {'Gains D1':<12} "
                 f"{'AUC':<10} {'KS':<10}")
    lines.append("-" * 75)
    for _, row in comparison_df.iterrows():
        lines.append(
            f"{row['Rank']:<6} {row['Model']:<25} "
            f"{row['Lift_D1_Val']:<12.3f} {row['Gains_D1_Val']:<12.3f} "
            f"{row['AUC_Val']:<10.4f} {row['KS_Val']:<10.4f}"
        )
    return lines


def decile_analysis(decile_df, winner_name: str) -> list:
    lines = ["", "=" * 80, f"3. DECILE ANALYSIS — {winner_name}", "=" * 80, ""]
    lines.append(f"{'Decile':<8} {'Count':>8} {'Resp':>8} {'Resp%':>8} "
                 f"{'Lift':>8} {'Cum Gains':>10}")
    lines.append("-" * 55)
    for _, row in decile_df.iterrows():
        lines.append(
            f"{int(row['decile']):<8} {int(row['count']):>8,} "
            f"{int(row['responders']):>8,} "
            f"{row['response_rate']*100:>7.2f}% "
            f"{row['lift']:>8.3f} "
            f"{row['cum_gains']*100:>9.1f}%"
        )
    return lines


def feature_importance_section(importance_df) -> list:
    lines = ["", "=" * 80, "4. FEATURE IMPORTANCE (Top 30)", "=" * 80, ""]
    lines.append(f"{'Rank':<6} {'Feature':<45} {'Importance':<12} {'Portion'}")
    lines.append("-" * 75)
    for _, row in importance_df.iterrows():
        lines.append(
            f"{row['Rank']:<6} {str(row['Feature'])[:43]:<45} "
            f"{row['Importance']:<12.6f} {row['Portion']*100:.2f}%"
        )

    # Category breakdown
    tw    = importance_df[importance_df['Feature'].str.startswith('tw_')]['Portion'].sum() * 100
    lhi   = importance_df[importance_df['Feature'].str.startswith('lhi_')]['Portion'].sum() * 100
    other = 100 - tw - lhi
    lines += [
        "",
        "  Feature Importance by Category:",
        f"    TW (Propensity) Variables:        {tw:.1f}%",
        f"    LHI (Lifestyle/Interest) Variables: {lhi:.1f}%",
        f"    Other Variables:                  {other:.1f}%",
    ]
    return lines


def trait_analysis_section(trait_df, insights: dict) -> list:
    lines = ["", "=" * 80, "5. TRAIT ANALYSIS", "=" * 80, ""]
    lines.append(f"{'Feature':<40} {'Mean Resp':>10} {'Mean Non':>10} "
                 f"{'Diff':>10}  Direction")
    lines.append("-" * 85)
    for _, row in trait_df.iterrows():
        lines.append(
            f"{str(row['Feature'])[:38]:<40} "
            f"{row['Mean_Responders']:>10.3f} "
            f"{row['Mean_Non_Responders']:>10.3f} "
            f"{row['Difference']:>+10.3f}  {row['Trait_Direction']}"
        )

    lines += ["", "  Strongest Positive Indicators:"]
    for r in insights['positive']:
        lines.append(f"    + {r['Feature']}: resp avg {r['Mean_Responders']:.2f} "
                     f"vs non-resp avg {r['Mean_Non_Responders']:.2f}")
    lines += ["", "  Strongest Negative Indicators:"]
    for r in insights['negative']:
        lines.append(f"    - {r['Feature']}: resp avg {r['Mean_Responders']:.2f} "
                     f"vs non-resp avg {r['Mean_Non_Responders']:.2f}")
    return lines


def model_explanation(winner_name: str) -> list:
    descriptions = {
        'Random Forest':      [
            "Ensemble of decision trees trained on random subsets of data.",
            "Each tree votes; majority wins. Robust to overfitting.",
        ],
        'XGBoost':            [
            "Gradient boosted decision trees built sequentially.",
            "Each tree corrects errors of the previous. Top performer for tabular data.",
        ],
        'CatBoost':           [
            "Gradient boosted trees optimised for categorical features.",
            "Handles categorical variables natively. Strong on mixed-type data.",
        ],
        'Logistic Regression':[
            "Linear model predicting log-odds of response.",
            "Highly interpretable. Fast reliable baseline.",
        ],
        'Gradient Boosting':  [
            "Sequential ensemble that corrects prior errors.",
            "Similar to XGBoost but uses sklearn implementation.",
        ],
    }
    desc = descriptions.get(winner_name, ["Ensemble or linear model."])
    lines = ["", "=" * 80, f"6. ABOUT {winner_name.upper()}", "=" * 80, ""]
    for d in desc:
        lines.append(f"  {d}")
    lines += [
        "",
        "  Metrics Guide:",
        "    Lift:  How many times better than random. 2.0 = 2x better.",
        "    Gains: % of responders captured. 30% at D1 = top 10% has 30% of responders.",
        "    AUC:   0.5 = random, 1.0 = perfect. >0.7 acceptable, >0.8 good.",
        "    KS:    Max separation between responder and non-responder distributions.",
    ]
    return lines


def recommendations(decile_df) -> list:
    d1 = decile_df[decile_df['decile'] == 1]['cum_gains'].iloc[0] * 100
    d2 = decile_df[decile_df['decile'] == 2]['cum_gains'].iloc[0] * 100
    d3 = decile_df[decile_df['decile'] == 3]['cum_gains'].iloc[0] * 100
    return [
        "", "=" * 80, "7. RECOMMENDATIONS", "=" * 80,
        "",
        "  Targeting Strategy:",
        f"    Top 10%: Captures {d1:.1f}% of responders",
        f"    Top 20%: Captures {d2:.1f}% of responders",
        f"    Top 30%: Captures {d3:.1f}% of responders",
        "",
        "  Recommended Actions:",
        "    1. Use scoring code to score new leads",
        "    2. Prioritize leads with highest Prob(IsTarget==1)",
        "    3. Run cost-benefit analysis to pick optimal targeting depth",
        "    4. Monitor performance over time and retrain if lift degrades",
        "", "=" * 80, "END OF REPORT", "=" * 80,
    ]
