"""
Observable State Manager - Implements Observer pattern for state changes
Allows components to react to state changes without tight coupling
"""
from typing import Dict, List, Any, Optional
from .interfaces import IStateObserver, IStateSubject


class ObservableState(IStateSubject):
    """State manager that notifies observers of changes"""
    
    def __init__(self):
        self._observers: List[IStateObserver] = []
        self._state: Dict[str, Any] = {}
        
    def add_observer(self, observer: IStateObserver) -> None:
        """Add state observer"""
        if observer not in self._observers:
            self._observers.append(observer)
            
    def remove_observer(self, observer: IStateObserver) -> None:
        """Remove state observer"""
        if observer in self._observers:
            self._observers.remove(observer)
            
    def notify_observers(self, state_type: str, old_value: Any, new_value: Any) -> None:
        """Notify all observers of state change"""
        for observer in self._observers:
            try:
                observer.on_state_changed(state_type, old_value, new_value)
            except Exception as e:
                print(f"Warning: Observer notification failed: {e}")
                
    def set_state(self, key: str, value: Any) -> None:
        """Set state value and notify observers"""
        old_value = self._state.get(key)
        if old_value != value:
            self._state[key] = value
            self.notify_observers(key, old_value, value)
            
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get state value"""
        return self._state.get(key, default)
        
    def get_all_state(self) -> Dict[str, Any]:
        """Get all state values"""
        return self._state.copy()
        
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update multiple state values"""
        for key, value in updates.items():
            self.set_state(key, value)


class StateLogger(IStateObserver):
    """Observer that logs state changes"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        
    def on_state_changed(self, state_type: str, old_value: Any, new_value: Any) -> None:
        """Log state changes"""
        if self.enabled:
            print(f"🔄 State changed: {state_type} -> {old_value} to {new_value}")


class StateValidator(IStateObserver):
    """Observer that validates state changes"""
    
    def __init__(self):
        self.validation_rules: Dict[str, callable] = {}
        
    def add_validation_rule(self, state_type: str, validator: callable) -> None:
        """Add validation rule for state type"""
        self.validation_rules[state_type] = validator
        
    def on_state_changed(self, state_type: str, old_value: Any, new_value: Any) -> None:
        """Validate state changes"""
        if state_type in self.validation_rules:
            validator = self.validation_rules[state_type]
            if not validator(new_value):
                print(f"⚠️ Warning: Invalid state change for {state_type}: {new_value}")


class StateChangeTracker(IStateObserver):
    """Observer that tracks state change history"""
    
    def __init__(self, max_history: int = 100):
        self.max_history = max_history
        self.history: List[Dict[str, Any]] = []
        
    def on_state_changed(self, state_type: str, old_value: Any, new_value: Any) -> None:
        """Track state changes"""
        import time
        
        change_record = {
            'timestamp': time.time(),
            'state_type': state_type,
            'old_value': old_value,
            'new_value': new_value
        }
        
        self.history.append(change_record)
        
        # Keep history size manageable
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
    def get_history(self, state_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get state change history"""
        if state_type:
            return [record for record in self.history if record['state_type'] == state_type]
        return self.history.copy()
        
    def get_recent_changes(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent state changes"""
        return self.history[-count:] if self.history else []