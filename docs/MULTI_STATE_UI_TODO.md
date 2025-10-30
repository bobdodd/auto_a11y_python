# Multi-State Testing UI - Remaining Work

## What's Implemented

1. ✅ Backend multi-state support (TestResult model has state fields)
2. ✅ Script executor supports XPath and CSS selectors  
3. ✅ Script UI for creating/editing multi-state scripts
4. ✅ Page view route fetches all state results for a session
5. ✅ State selector buttons added to template

## What's Needed

The template (pages/view.html) currently shows only `latest_result`. We need to modify it to show results for ALL states when `state_results` has multiple entries.

### Current Structure

```html
<div class="card test-results-card">
    <!-- State selector buttons (lines 501-526) -->
    
    <div class="card-body">
        <!-- All violations/warnings/info for latest_result -->
        <!-- This section spans ~2500 lines -->
    </div>
</div>
```

### Needed Structure

```html
<div class="card test-results-card">
    <!-- State selector buttons (lines 501-526) - DONE -->
    
    {% if state_results and state_results|length > 1 %}
        <!-- Multi-state mode: render each state separately -->
        {% for state_result in state_results %}
        <div id="state-results-{{ loop.index0 }}" class="state-results card-body" 
             style="display: {% if loop.first %}block{% else %}none{% endif %};">
            <!-- Render violations/warnings/info for THIS state -->
            <!-- Copy entire results section, replace latest_result with state_result -->
        </div>
        {% endfor %}
    {% else %}
        <!-- Single state mode: show latest_result as before -->
        <div class="card-body">
            <!-- Existing results display -->
        </div>
    {% endif %}
</div>
```

### Implementation Options

**Option A: Macro Approach (Recommended)**
1. Extract the results rendering logic (lines ~528-2950) into a Jinja macro
2. Call the macro once for single-state, or loop for multi-state
3. Clean, maintainable, no code duplication

**Option B: Conditional Duplication**
1. Wrap existing code in {% if not state_results %}
2. Add {% else %} with loop over state_results
3. Copy the entire results section for each state
4. Quick but creates code duplication

**Option C: JavaScript Client-Side**
1. Pass all state_results as JSON to JavaScript
2. Render results client-side based on selected state
3. More complex, requires rewriting template logic in JS

### JavaScript Function Already Present

The `showState(stateIndex)` function is already defined (needs to be added to template):

```javascript
function showState(stateIndex) {
    document.querySelectorAll('.state-results').forEach(el => {
        el.style.display = 'none';
    });
    document.getElementById(`state-results-${stateIndex}`).style.display = 'block';
    
    document.querySelectorAll('.state-selector').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-state-index="${stateIndex}"]`).classList.add('active');
}
```

## Next Steps

1. Choose implementation approach (Macro recommended)
2. Extract results rendering to macro if using Option A
3. Update template to handle both single and multi-state
4. Add showState() JavaScript function
5. Test with actual multi-state test results

