# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

My initial design consists of four classes. Owner stores the owner's name and daily time available. Pet stores the pet's name and species. Task stores a task's title, duration in minutes, and priority level. Scheduler takes an Owner, a Pet, and a list of Tasks as input and produces an ordered daily plan by sorting tasks by priority and checking that total duration fits within the owner's available time.

- What classes did you include, and what responsibilities did you assign to each?

- Owner: stores owner name and available time per day (in minutes) to be used by the Scheduler for the time budget

- Pet: stores pet name and species to be passed into the Scheduler for context in the output

- Task: stores task title, duration (minutes), and priority (low/medium/high) to be used by the Scheduler for operation

- Scheduler: takes an Owner, Pet, and list of Tasks, sorts tasks by priority,filters out tasks that don't fit in available time, and returns an ordered daily plan with reasoning

**b. Design changes**

- Did your design change during implementation? yes
- If yes, describe at least one change and why you made it.

The Scheduler now has self.remaining_minutes which starts at owner.available_minutes and gets decremented in generate_plan() to track the time budget properly

Why? initially has_time_for() function doesn't track the remaining time and available_time never decreases , so calling it twice with 2 tasks could say yes to both even if they exceed the budget


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

The conflict detector checks for exact scheduled_time matches (e.g., both tasks say 08:00) than checking whether task durations overlap (e.g., a 30-minute task at 08:00 and a 20-minute task at 08:15 would overlap in real life but undetected).

This is a reasonable  because pet care tasks are typically assigned to named time slots like "morning walk," "breakfast," "evening meds"  than precise start times down to the minute. Implementing full duration-overlap detection would require converting HH:MM strings into comparable time objects, calculating end times, and checking range intersections which is more complex given how pet owners actually plan their day.

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
