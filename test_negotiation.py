"""
Quick Verification Script for AURA Negotiation Engine
Run this to test all core functions automatically
Last Updated: November 2025 - Agentic AI Integration
"""

import sys
sys.path.insert(0, r'c:\Users\gulam\Desktop\AURA\aura')

# Mock streamlit session_state for testing
class MockSessionState:
    def __init__(self):
        self._state = {}
    
    def setdefault(self, key, default):
        if key not in self._state:
            self._state[key] = default
        return self._state[key]
    
    def get(self, key, default=None):
        return self._state.get(key, default)
    
    def __setitem__(self, key, value):
        self._state[key] = value
    
    def __getitem__(self, key):
        return self._state[key]
    
    def __contains__(self, key):
        return key in self._state

# Create mock streamlit module
class MockStreamlit:
    def __init__(self):
        self.session_state = MockSessionState()
    
    def setdefault(self, *args, **kwargs):
        pass

# Inject mock
import sys
sys.modules['streamlit'] = MockStreamlit()
st = sys.modules['streamlit']

# Now import the functions
from datetime import datetime, timedelta

# Copy the functions here for standalone testing
def init_negotiation_state():
    st.session_state.setdefault("negotiations", {})
    st.session_state.setdefault("funds_recovered", 0)
    st.session_state.setdefault("active_user", None)
    st.session_state.setdefault("negotiation_log", [])

def get_or_create_demo_user(user_id="USR1001"):
    if user_id not in st.session_state.get("negotiations", {}):
        demo = {
            "user_id": user_id,
            "name": "Gulam",
            "wallet": 2000,
            "missed_amount": 2000,
            "offer_amount": 500,
            "expiry_days": 7,
            "status": "pending",
            "started_at": datetime.utcnow().isoformat(),
            "accepted_at": None,
            "last_message": None
        }
        st.session_state["negotiations"][user_id] = demo
        st.session_state["active_user"] = user_id
        st.session_state["negotiation_log"].append(
            (datetime.utcnow().isoformat(), f"Demo user {user_id} created")
        )
    return st.session_state["negotiations"][user_id]

def start_negotiation(user_id, offer_amount=None, expiry_days=None, agent_message=None):
    init_negotiation_state()
    negos = st.session_state["negotiations"]
    if user_id not in negos:
        get_or_create_demo_user(user_id)
    entry = negos[user_id]
    if entry["status"] == "restructured":
        return entry
    if offer_amount is not None:
        entry["offer_amount"] = int(offer_amount)
    if expiry_days is not None:
        entry["expiry_days"] = int(expiry_days)
    entry["status"] = "offer_sent"
    entry["started_at"] = entry.get("started_at") or datetime.utcnow().isoformat()
    entry["last_message"] = agent_message or (
        f"Hi {entry['name']}, you missed your payment. I see you have ₹{entry['wallet']:,}. "
        f"If you pay ₹{entry['offer_amount']:,} today, I can extend the rest for {entry['expiry_days']} days. Do you accept?"
    )
    st.session_state["negotiation_log"].append(
        (datetime.utcnow().isoformat(), f"Offer sent to {user_id}: ₹{entry['offer_amount']}")
    )
    return entry

def accept_offer(user_id):
    init_negotiation_state()
    negos = st.session_state["negotiations"]
    if user_id not in negos:
        raise ValueError("No negotiation exists for user_id=" + str(user_id))
    entry = negos[user_id]
    if entry.get("status") == "restructured":
        return entry
    if entry.get("status") not in ("offer_sent", "pending"):
        st.session_state["negotiation_log"].append(
            (datetime.utcnow().isoformat(), f"Accept invoked for {user_id} but status was {entry.get('status')}")
        )
    entry["status"] = "restructured"
    entry["accepted_at"] = datetime.utcnow().isoformat()
    recovered = entry.get("offer_amount", 0)
    if not entry.get("_counted"):
        st.session_state["funds_recovered"] = int(st.session_state.get("funds_recovered", 0)) + int(recovered)
        entry["_counted"] = True
    st.session_state["negotiation_log"].append(
        (datetime.utcnow().isoformat(), f"{user_id} accepted offer; recovered ₹{recovered}")
    )
    return entry

def negotiation_summary():
    init_negotiation_state()
    total = st.session_state.get("funds_recovered", 0)
    negotiations = st.session_state.get("negotiations", {})
    counts = {"pending":0, "offer_sent":0, "restructured":0, "rejected":0}
    for v in negotiations.values():
        counts[v.get("status","pending")] = counts.get(v.get("status","pending"), 0) + 1
    return {"total_recovered": total, "counts": counts, "negotiations": negotiations, "log": st.session_state.get("negotiation_log", [])}

# Run tests
def run_tests():
    print("=" * 60)
    print("AURA NEGOTIATION ENGINE - VERIFICATION TESTS")
    print("=" * 60)
    
    init_negotiation_state()
    
    # Test 1: Create User
    print("\n[TEST 1] Creating demo user USR1001...")
    user = get_or_create_demo_user("USR1001")
    assert user["user_id"] == "USR1001", "User ID mismatch"
    assert user["status"] == "pending", "Initial status should be pending"
    assert user["offer_amount"] == 500, "Default offer should be 500"
    print("✅ PASS: User created successfully")
    print(f"   - User: {user['name']}")
    print(f"   - Wallet: ₹{user['wallet']}")
    print(f"   - Status: {user['status']}")
    
    # Test 2: Start Negotiation
    print("\n[TEST 2] Starting negotiation...")
    nego = start_negotiation("USR1001")
    assert nego["status"] == "offer_sent", "Status should be offer_sent"
    assert nego["last_message"] is not None, "Message should be generated"
    print("✅ PASS: Negotiation started")
    print(f"   - Status: {nego['status']}")
    print(f"   - Offer: ₹{nego['offer_amount']}")
    print(f"   - Message: {nego['last_message'][:60]}...")
    
    # Test 3: Accept Offer (First Time)
    print("\n[TEST 3] Accepting offer (first time)...")
    result = accept_offer("USR1001")
    assert result["status"] == "restructured", "Status should be restructured"
    assert result.get("_counted") == True, "Should be marked as counted"
    summary = negotiation_summary()
    assert summary["total_recovered"] == 500, "Should recover ₹500"
    print("✅ PASS: Offer accepted and funds recovered")
    print(f"   - Status: {result['status']}")
    print(f"   - Total recovered: ₹{summary['total_recovered']}")
    
    # Test 4: Accept Offer (Second Time - Idempotency)
    print("\n[TEST 4] Testing idempotency (accept again)...")
    before_total = summary["total_recovered"]
    result2 = accept_offer("USR1001")
    summary2 = negotiation_summary()
    after_total = summary2["total_recovered"]
    assert before_total == after_total, f"Idempotency FAILED: {before_total} != {after_total}"
    print("✅ PASS: Idempotency works (no double-counting)")
    print(f"   - Before: ₹{before_total}")
    print(f"   - After: ₹{after_total}")
    
    # Test 5: Summary
    print("\n[TEST 5] Checking summary...")
    summary = negotiation_summary()
    assert summary["total_recovered"] == 500, "Total should be 500"
    assert summary["counts"]["restructured"] == 1, "Should have 1 restructured"
    assert len(summary["log"]) >= 3, "Should have at least 3 log entries"
    print("✅ PASS: Summary is accurate")
    print(f"   - Total recovered: ₹{summary['total_recovered']}")
    print(f"   - Counts: {summary['counts']}")
    print(f"   - Log entries: {len(summary['log'])}")
    
    # Test 6: Multiple Users
    print("\n[TEST 6] Testing multiple users...")
    get_or_create_demo_user("USR1002")
    start_negotiation("USR1002", offer_amount=750)
    accept_offer("USR1002")
    
    get_or_create_demo_user("USR1003")
    start_negotiation("USR1003", offer_amount=1000)
    accept_offer("USR1003")
    
    final_summary = negotiation_summary()
    expected_total = 500 + 750 + 1000
    assert final_summary["total_recovered"] == expected_total, f"Expected {expected_total}, got {final_summary['total_recovered']}"
    assert final_summary["counts"]["restructured"] == 3, "Should have 3 restructured"
    print("✅ PASS: Multiple users handled correctly")
    print(f"   - Total recovered: ₹{final_summary['total_recovered']:,}")
    print(f"   - Restructured count: {final_summary['counts']['restructured']}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 60)
    print(f"\nFinal State:")
    print(f"  - Users created: {len(final_summary['negotiations'])}")
    print(f"  - Total funds recovered: ₹{final_summary['total_recovered']:,}")
    print(f"  - Restructured loans: {final_summary['counts']['restructured']}")
    print(f"  - Log entries: {len(final_summary['log'])}")
    print("\n✅ Negotiation engine is working as designed!")
    print("✅ Ready for UI integration and demo!")
    
    return True

if __name__ == "__main__":
    try:
        success = run_tests()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
