#!/usr/bin/env python3
"""
Test Results Comparison Script
Compares results from original and improved test scripts
"""

import json
import os
from datetime import datetime
from typing import Dict, Any

def load_test_results(filename: str) -> Dict[str, Any]:
    """Load test results from JSON file"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

def compare_test_results():
    """Compare original and improved test results"""
    print("🔍 Test Scripts Comparison Report")
    print("=" * 50)
    
    # Load results
    original_results = load_test_results("/home/sa/projects/n8n_sec/test-results.json")
    improved_results = load_test_results("/home/sa/projects/n8n_sec/improved-test-results.json")
    
    if not original_results:
        print("❌ Original test results not found")
        return
    
    if not improved_results:
        print("❌ Improved test results not found")
        return
    
    # Compare summaries
    print("\n📊 Summary Comparison:")
    print("-" * 30)
    
    orig_summary = original_results.get('summary', {})
    impr_summary = improved_results.get('summary', {})
    
    print(f"{'Metric':<20} {'Original':<12} {'Improved':<12} {'Change':<10}")
    print("-" * 60)
    
    metrics = ['passed', 'failed', 'warnings', 'total', 'success_rate']
    for metric in metrics:
        orig_val = orig_summary.get(metric, 0)
        impr_val = impr_summary.get(metric, 0)
        
        if metric == 'success_rate':
            change = f"+{impr_val - orig_val:.1f}%" if impr_val > orig_val else f"{impr_val - orig_val:.1f}%"
            print(f"{metric:<20} {orig_val:.1f}%{'':<7} {impr_val:.1f}%{'':<7} {change:<10}")
        else:
            change = f"+{impr_val - orig_val}" if impr_val > orig_val else str(impr_val - orig_val)
            print(f"{metric:<20} {orig_val:<12} {impr_val:<12} {change:<10}")
    
    # Analyze failed tests
    print("\n❌ Failed Tests Analysis:")
    print("-" * 30)
    
    orig_failed = [r['test_name'] for r in original_results.get('detailed_results', []) if r['status'] == 'FAIL']
    impr_failed = [r['test_name'] for r in improved_results.get('detailed_results', []) if r['status'] == 'FAIL']
    
    print(f"Original failed tests ({len(orig_failed)}):")
    for test in orig_failed:
        print(f"  • {test}")
    
    print(f"\nImproved failed tests ({len(impr_failed)}):")
    if impr_failed:
        for test in impr_failed:
            print(f"  • {test}")
    else:
        print("  ✅ No failed tests!")
    
    # Show improvements
    resolved_issues = set(orig_failed) - set(impr_failed)
    if resolved_issues:
        print(f"\n✅ Resolved Issues ({len(resolved_issues)}):")
        for test in resolved_issues:
            print(f"  • {test}")
    
    # Show warnings
    print("\n⚠️ Warnings Analysis:")
    print("-" * 30)
    
    orig_warnings = [r for r in original_results.get('detailed_results', []) if r['status'] == 'WARN']
    impr_warnings = [r for r in improved_results.get('detailed_results', []) if r['status'] == 'WARN']
    
    print(f"Original warnings: {len(orig_warnings)}")
    print(f"Improved warnings: {len(impr_warnings)}")
    
    if impr_warnings:
        print("\nCurrent warnings:")
        for warning in impr_warnings:
            print(f"  • {warning['test_name']}: {warning['details']}")
    
    # Key insights
    print("\n🔑 Key Insights:")
    print("-" * 30)
    
    success_improvement = impr_summary.get('success_rate', 0) - orig_summary.get('success_rate', 0)
    
    if success_improvement > 0:
        print(f"✅ Success rate improved by {success_improvement:.1f}%")
    
    if len(resolved_issues) > 0:
        print(f"✅ Resolved {len(resolved_issues)} previously failing tests")
    
    if len(impr_failed) == 0:
        print("✅ No functional failures detected in improved tests")
    
    if len(impr_warnings) > 0:
        print(f"⚠️ {len(impr_warnings)} configuration issues identified (not functional failures)")
    
    # Recommendations
    recommendations = improved_results.get('recommendations', [])
    if recommendations:
        print("\n💡 Recommendations:")
        print("-" * 30)
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    print("\n" + "=" * 50)
    print("📋 Conclusion:")
    
    if success_improvement > 20:
        print("🎉 Significant improvement in test accuracy detected!")
        print("   The improved test script provides much more reliable results.")
    elif success_improvement > 0:
        print("✅ Test accuracy improved with better diagnostics.")
    
    if len(impr_failed) == 0:
        print("✅ All core functionality appears to be working correctly.")
        if len(impr_warnings) > 0:
            print("⚠️ Some configuration adjustments needed (see warnings above).")
    
    print(f"\n📅 Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    compare_test_results()