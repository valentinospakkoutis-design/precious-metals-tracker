"""
Accuracy Tracking System
Logs predictions and tracks accuracy over time
"""

import json
import os
from datetime import datetime
from pathlib import Path

class AccuracyTracker:
    def __init__(self, storage_path="data/predictions_log.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self.predictions = self.load_predictions()
    
    def load_predictions(self):
        """Load existing predictions from file"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_predictions(self):
        """Save predictions to file"""
        with open(self.storage_path, 'w') as f:
            json.dump(self.predictions, f, indent=2)
    
    def log_prediction(self, asset_id, predicted_price, predicted_change_pct, 
                      current_price, horizon_minutes, confidence):
        """Log a new prediction"""
        prediction = {
            'id': len(self.predictions) + 1,
            'asset_id': asset_id,
            'predicted_at': datetime.now().isoformat(),
            'horizon_minutes': horizon_minutes,
            'current_price': current_price,
            'predicted_price': predicted_price,
            'predicted_change_pct': predicted_change_pct,
            'confidence': confidence,
            'actual_price': None,
            'actual_change_pct': None,
            'was_correct': None,
            'error_pct': None,
            'checked_at': None
        }
        
        self.predictions.append(prediction)
        self.save_predictions()
        
        return prediction['id']
    
    def update_actual(self, prediction_id, actual_price):
        """Update prediction with actual outcome"""
        for pred in self.predictions:
            if pred['id'] == prediction_id:
                pred['actual_price'] = actual_price
                pred['actual_change_pct'] = ((actual_price - pred['current_price']) / 
                                            pred['current_price']) * 100
                
                # Check if prediction was correct (same direction)
                pred_direction = 1 if pred['predicted_change_pct'] > 0 else -1
                actual_direction = 1 if pred['actual_change_pct'] > 0 else -1
                pred['was_correct'] = (pred_direction == actual_direction)
                
                # Calculate error
                pred['error_pct'] = abs(pred['predicted_change_pct'] - pred['actual_change_pct'])
                pred['checked_at'] = datetime.now().isoformat()
                
                self.save_predictions()
                return True
        
        return False
    
    def get_accuracy_stats(self, asset_id=None, hours=24):
        """Calculate accuracy statistics"""
        # Filter predictions
        cutoff_time = datetime.now()
        
        filtered = []
        for pred in self.predictions:
            if pred['was_correct'] is not None:  # Only completed predictions
                if asset_id is None or pred['asset_id'] == asset_id:
                    filtered.append(pred)
        
        if not filtered:
            return None
        
        total = len(filtered)
        correct = sum(1 for p in filtered if p['was_correct'])
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        # Calculate average error
        errors = [p['error_pct'] for p in filtered if p['error_pct'] is not None]
        avg_error = sum(errors) / len(errors) if errors else 0
        
        # Per horizon breakdown
        horizons = {}
        for pred in filtered:
            h = pred['horizon_minutes']
            if h not in horizons:
                horizons[h] = {'total': 0, 'correct': 0}
            horizons[h]['total'] += 1
            if pred['was_correct']:
                horizons[h]['correct'] += 1
        
        horizon_accuracy = {}
        for h, stats in horizons.items():
            horizon_accuracy[h] = (stats['correct'] / stats['total']) * 100
        
        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy_pct': round(accuracy, 2),
            'avg_error_pct': round(avg_error, 2),
            'horizon_accuracy': horizon_accuracy
        }


def demo_accuracy_tracking():
    """Demo the accuracy tracker"""
    print("=" * 70)
    print("📊 ACCURACY TRACKING SYSTEM - Demo")
    print("=" * 70)
    print()
    
    tracker = AccuracyTracker(storage_path="demo_predictions.json")
    
    # Simulate some predictions
    print("📝 Logging predictions...")
    
    predictions_to_log = [
        ('BTC', 113000, +0.5, 112500, 10, 85),
        ('BTC', 113500, +0.9, 112500, 20, 78),
        ('ETH', 4050, +1.0, 4010, 10, 82),
        ('GOLD', 4100, +1.5, 4040, 30, 75),
    ]
    
    prediction_ids = []
    for asset, pred_price, pred_change, curr_price, horizon, conf in predictions_to_log:
        pred_id = tracker.log_prediction(asset, pred_price, pred_change, 
                                        curr_price, horizon, conf)
        prediction_ids.append(pred_id)
        print(f"   ✅ Logged prediction #{pred_id} for {asset}: {pred_change:+.1f}%")
    
    # Simulate checking results
    print(f"\n⏱️  Simulating results after {predictions_to_log[0][4]} minutes...")
    
    # Simulate actual outcomes
    actual_outcomes = [
        (prediction_ids[0], 112800),  # BTC went up (correct!)
        (prediction_ids[1], 112300),  # BTC went down (wrong!)
        (prediction_ids[2], 4025),    # ETH went up (correct!)
        (prediction_ids[3], 4080),    # GOLD went up (correct!)
    ]
    
    for pred_id, actual_price in actual_outcomes:
        tracker.update_actual(pred_id, actual_price)
    
    print("   ✅ Results updated!")
    
    # Show accuracy stats
    print(f"\n📈 ACCURACY STATISTICS:")
    print("-" * 70)
    
    # Overall
    stats = tracker.get_accuracy_stats()
    if stats:
        print(f"\n   Overall Performance:")
        print(f"   • Total Predictions: {stats['total_predictions']}")
        print(f"   • Correct: {stats['correct_predictions']}/{stats['total_predictions']}")
        print(f"   • Accuracy: {stats['accuracy_pct']}%")
        print(f"   • Avg Error: {stats['avg_error_pct']:.2f}%")
        
        print(f"\n   By Horizon:")
        for horizon, acc in stats['horizon_accuracy'].items():
            print(f"   • {horizon} min: {acc:.1f}% accuracy")
    
    # Per asset
    print(f"\n   By Asset:")
    for asset in ['BTC', 'ETH', 'GOLD']:
        asset_stats = tracker.get_accuracy_stats(asset_id=asset)
        if asset_stats:
            print(f"   • {asset:6} {asset_stats['accuracy_pct']:.0f}% "
                  f"({asset_stats['correct_predictions']}/{asset_stats['total_predictions']})")
    
    print("\n" + "=" * 70)
    print("✅ Accuracy Tracking Demo Complete!")
    print("\n💡 In production:")
    print("   • Track every prediction automatically")
    print("   • Check outcomes after horizon time")
    print("   • Display accuracy dashboard in app")
    print("   • Alert if accuracy drops below threshold")
    print("=" * 70)
    
    # Cleanup demo file
    import os
    if os.path.exists("demo_predictions.json"):
        os.remove("demo_predictions.json")


if __name__ == "__main__":
    demo_accuracy_tracking()
