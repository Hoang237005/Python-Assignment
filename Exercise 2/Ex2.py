import os
import pandas as pd
import matplotlib.pyplot as plt


def extract_extremes(data, metric):
    """Retrieve top and bottom performers for a given metric"""
    clean_data = data[['Player', 'Team', metric]].dropna()
    top_performers = clean_data.nlargest(3, metric)
    bottom_performers = clean_data.nsmallest(3, metric)
    return top_performers, bottom_performers


def generate_statistical_report(data, numerical_fields):
    """Generate comprehensive statistical report"""
    overall_medians = data[numerical_fields].median()
    overall_means = data[numerical_fields].mean()
    overall_stds = data[numerical_fields].std()

    team_metrics = data.groupby('Team')[numerical_fields].agg(['median', 'mean', 'std'])
    team_metrics.columns = [f'{func.capitalize()} of {stat}'
                            for stat, func in team_metrics.columns]
    team_metrics = team_metrics.reset_index()

    overall_stats = {'Team': 'All'}
    for field in numerical_fields:
        overall_stats[f'Median of {field}'] = overall_medians[field]
        overall_stats[f'Mean of {field}'] = overall_means[field]
        overall_stats[f'Std of {field}'] = overall_stds[field]

    combined_report = pd.concat([
        pd.DataFrame([overall_stats]),
        team_metrics
    ], ignore_index=True)

    combined_report['Index'] = range(len(combined_report))
    stat_columns = [col for col in combined_report.columns
                    if col not in ['Index', 'Team']]

    return combined_report[['Index', 'Team'] + stat_columns]


def visualize_distributions(data, metrics, team_field='Team'):
    """Generate distribution visualizations for specified metrics"""
    if not os.path.exists('Exercise 2/histograms'):
        os.makedirs('Exercise 2/histograms')

    for metric in metrics:
        # Global distribution
        data[metric].hist(bins=20)
        plt.title(f'Distribution of {metric} (All Players)')
        plt.xlabel(metric)
        plt.ylabel('Count')
        plt.savefig(f'Exercise 2/histograms/hist_all_{metric}.png')
        plt.close()

        # Team-specific distributions
        for team in data[team_field].unique():
            team_data = data[data[team_field] == team]
            team_data[metric].hist(bins=20)
            plt.title(f'Distribution of {metric} - {team}')
            plt.xlabel(metric)
            plt.ylabel('Count')
            safe_name = team.replace(" ", "_").replace("/", "_")
            plt.savefig(f'Exercise 2/histograms/hist_{safe_name}_{metric}.png')
            plt.close()


def identify_peak_performers(data, numerical_fields):
    """Determine teams with highest average for each metric"""
    team_averages = data.groupby('Team')[numerical_fields].mean()
    findings = []

    for field in numerical_fields:
        peak_value = team_averages[field].max()
        if pd.notna(peak_value) and peak_value != 0:
            leading_team = team_averages[field].idxmax()
            findings.append(
                f"Metric: {field}, Leading Team: {leading_team}, "
                f"Average: {peak_value:.2f}"
            )

    return findings


def main():
    # Data preparation
    player_data = pd.read_csv('Exercise 1/result.csv', na_values=['N/a'])
    player_data.drop(columns=["Age"], inplace=True)
    player_data.replace("N/a", pd.NA, inplace=True)

    numerical_fields = player_data.select_dtypes(include=['number']).columns

    # Generate top performers report
    with open('Exercise 2/top_3.txt', 'w', encoding='utf-8') as output_file:
        for metric in numerical_fields:
            top, bottom = extract_extremes(player_data, metric)
            output_file.write(f"Metric: {metric}\nTop Performers:\n")
            for rank, (_, row) in enumerate(top.iterrows(), 1):
                output_file.write(f" {rank}. {row['Player']} ({row['Team']}): {row[metric]}\n")
            output_file.write("Lowest Performers:\n")
            for rank, (_, row) in enumerate(bottom.iterrows(), 1):
                output_file.write(f" {rank}. {row['Player']} ({row['Team']}): {row[metric]}\n")
            output_file.write("\n")
    print("Performance analysis saved to top_3.txt")

    # Generate statistical report
    stats_report = generate_statistical_report(player_data, numerical_fields)
    stats_report.to_csv('Exercise 2/results2.csv', index=False)
    print("Statistical report saved to results2.csv")

    # Create visualizations
    offensive_metrics = ['Goals', 'Assists', 'xG']
    defensive_metrics = ['Tkl', 'Blocks', 'Int']
    visualize_distributions(player_data, offensive_metrics + defensive_metrics)
    print("Distribution visualizations saved in 'histograms' directory")

    # Identify top-performing teams
    peak_performers = identify_peak_performers(player_data, numerical_fields)
    with open('Exercise 2/highest_team_stats.txt', 'w') as report_file:
        report_file.write("Teams with Highest Average Performance by Metric\n")
        report_file.write("=" * 50 + "\n\n")
        report_file.write("\n".join(peak_performers))
    print("Team performance analysis saved to highest_team_stats.txt")


if __name__ == "__main__":
    main()