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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
