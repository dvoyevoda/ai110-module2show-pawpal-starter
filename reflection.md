# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Three core actions this app should contain is:
1. Allow a user to enter basic owner + pet info
2. Add/edit tasks
3. Generate a schedule
Classes would be, Owner, Pet, Task, Schedule

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. Owner now holds a list of Pet objects and Pet now holds a list of Task objects, so the code actually reflects the relationships defined in the UML diagram. generate_schedule() also received a preferences parameter because the README requires the scheduler to consider owner preferences, and without it the method would have had no way to access that data when implemented.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three main constraints: the owner's available time (hard cap in minutes), each task's priority (1–5), and the owner's preferred categories (which get a +2 priority boost). Time had to come first because you physically can't do more than you have time for. Priority came next because skipping a medication is worse than skipping a play session. Preferences came last as a tiebreaker — if two tasks have similar priority, the one the owner cares about more should win.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses a greedy algorithm instead of an optimal knapsack solver. This means it picks the highest-priority task first and keeps going until time runs out, which can occasionally miss a better combination (e.g., two medium tasks that together beat one large task). This is a reasonable tradeoff because a pet owner's task list is small — usually under 10–15 items — so the greedy result is close to optimal in practice, and the simplicity makes the logic easy to understand and debug.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI for brainstorming, debugging, and polishing the code/UI.

- For design, I asked for feedback on class responsibilities and method names.
- For debugging, I asked why specific behaviors failed and what to test next.
- For refactoring, I asked how to simplify repeated logic and improve readability.

The most helpful prompts were specific ones, like:
- "What edge cases should I test for recurring tasks?"
- "Why is this conflict detection rule missing warnings?"
- "How can I clean up this UI code without changing behavior?"

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One time, I got a suggestion that added extra complexity to scheduling logic that I did not need for this scope. I did not copy it directly.

Instead, I kept the simpler greedy logic and verified it with tests. I only accepted changes that passed tests and matched the project requirements.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the most important scheduling behaviors:

- Sorting tasks by time slot
- Recurring task creation when a task is completed
- Conflict detection warnings
- Schedule packing within available time
- Priority and preference effects on task selection

These tests were important because they cover the core logic of the app. If these fail, the schedule can become unrealistic or misleading.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am fairly confident (about 4/5) that the scheduler works correctly for normal use cases.

If I had more time, I would test:
- very large task lists
- more unusual input values
- more UI-level integration cases
- cases where many tasks have the same priority and time slot

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied with the overall structure and test coverage. The class design is clean, and the scheduler behavior is understandable.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In another iteration, I would add full task editing/deleting in the UI and save data to a database so user data persists between sessions. I would also improve schedule visualization, like showing a timeline view.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My biggest takeaway is that clear structure plus testing makes development much easier. AI helped me move faster, but I still needed to verify every suggestion with logic checks and tests.

---

## 🖥️ Demo

<a href="/course_images/ai110/ui.png" target="_blank">
  <img src="/course_images/ai110/ui.png" alt="PawPal+ UI screenshot" />
</a>
