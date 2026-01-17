---
title: "Solving the \"Impossible\" in ClickHouse: Advent of Code 2025"
date: "2025-12-31T12:33:35.429Z"
author: "Zach Naimon"
category: "Engineering"
excerpt: "At ClickHouse, we don't like the word \"impossible.\" We believe that with the right tools, everything is a data problem. To prove it, we decided to complete the 2025 Advent of Code unconventionally: using pure ClickHouse SQL."
---

# Solving the "Impossible" in ClickHouse: Advent of Code 2025

## Introduction

Every December, the programming community gathers for a collective ritual: [Advent of Code](https://adventofcode.com/). Created by Eric Wastl, it is an Advent calendar of small programming puzzles that releases a new challenge every day from December 1st through the 12th.

These aren't your typical "fix the bug" or "build an API" tasks. They are algorithmic challenges that require complex data structures, graph traversal, 3D geometry, cellular automata simulations, and pathfinding algorithms. Naturally, developers usually reach for general-purpose languages like Python, Rust, Go, or C++ to solve them.

### Why not SQL?

Asking a database to solve these problems is generally considered a mistake. Standard SQL is a declarative language designed for retrieving and aggregating relational data, not for imperative game loops or complex state management. It lacks native support for the data structures usually required for these puzzles (like stacks, queues, or trees), and attempting to solve them with standard JOINs usually leads to performance disasters or syntax errors. In short, solving Advent of Code in SQL is widely considered "impossible" - or at least, incredibly painful.

### The ClickHouse approach

At ClickHouse, we don't like the word "impossible." We believe that with the right tools, **everything** is a data problem. ClickHouse isn't just a fast OLAP database; it is a vectorized query engine with a massive library of analytical functions that can be ~~abused~~ bent to solve general-purpose computing problems.

To prove it, we decided to complete the 2025 Advent of Code unconventionally: using **pure ClickHouse SQL**.

### The rules

To ensure we didn't take any shortcuts, we imposed three strict rules on our solutions:

1. **Pure ClickHouse SQL only**: we allowed absolutely no User Defined Functions (UDFs), and specifically no _executable_ UDFs that would allow us to "cheat" by shelling out to Python or Bash. If the query engine couldn't do it natively, we couldn't do it.

2. **Raw inputs only**: in Advent of Code, the input is often a messy text file.  Sometimes a list of numbers, sometimes an ASCII art map, or a block of cryptic instructions. We were not allowed to pre-process this data. The solution query must accept the raw puzzle input string exactly as provided by the AoC challenge and parse it within the query.

3. **"Single query" constraint**: this is the hardest rule of all. We were not allowed to create tables, materialized views, or temporary tables to store intermediate state. The entire puzzle—from parsing the input, to solving Part 1, to solving the (often substantially more complex) Part 2—must be executed as a **single, atomic query**. This required us to rely heavily on CTEs to chain our logic together in one uninterrupted execution.

Below are the solutions for all 12 days of Advent of Code 2025, demonstrating how we turned "impossible" algorithmic challenges into pure ClickHouse SQL queries.

>Note: in order to comply with Advent of Code's distribution policy, the queries below use a wrapper `URL()` table to fetch the raw puzzle inputs without exposing them. The original query versions with handling for direct string inputs can be found in our [ClickHouse/TreeHouse](https://github.com/ClickHouse/TreeHouse) repository.

## Day 1: The Secret Entrance

**The Puzzle**: The elves have locked their secret entrance with a rotating dial safe. The puzzle involves simulating the movement of a dial labeled 0-99 based on a sequence of instructions like L68 (turn left 68 clicks) or R48 (turn right 48 clicks).

- **Part 1** asks for the final position of the dial after all rotations, starting from 50.
- **Part 2** requires a more complex simulation: counting exactly how many times the dial points to 0 _during_ the entire process, including intermediate clicks as it rotates past zero multiple times.

**How we solved this in ClickHouse SQL:** We treated this simulation as a stream processing problem rather than a procedural loop. Since the state of the dial depends entirely on the history of moves, we can calculate the cumulative position for every single instruction at once. We parsed the directions into positive (Right) and negative (Left) integers, then used a window function to create a running total of steps. For Part 2, where we needed to detect "zero crossings," we compared the current running total with the previous row's total to determine if the dial passed 0.

**Implementation details:**

1. [`sum() OVER (...)`](https://clickhouse.com/docs/en/sql-reference/window-functions): We used standard SQL window functions to maintain the "running total" of the dial's position. By normalizing the left/right directions into positive/negative values, we tracked the cumulative position for every row in a single pass.

```sql
sum(normalized_steps) OVER (ORDER BY instruction_id) AS raw_position
```

2. [`lagInFrame`](https://clickhouse.com/docs/en/sql-reference/window-functions): To count how many times we passed zero, we needed to know where the dial started before the current rotation. We used `lagInFrame` to peek at the position from the previous row. This allowed us to compare the start and end points of a rotation and mathematically determine if 0 fell between them.

**Full Solution:**



```sql
WITH
--Fetch puzzle input
input_wrapper AS (SELECT raw_blob AS input FROM aoc.input1),

-- Parse the input string into individual instructions
parsed_instructions AS (
    -- Initial placeholder row
    SELECT
        0 AS instruction_id,
        'R50' AS raw_instruction,
        'R' AS direction,
        50::Int16 AS steps
    
    UNION ALL
    
    -- Parse each line from input
    SELECT
        rowNumberInAllBlocks() + 1 AS instruction_id,
        raw AS raw_instruction,
        substring(raw, 1, 1) AS direction,
        substring(raw, 2)::Int16 AS steps
    FROM format(TSV, 'raw String', (SELECT input FROM input_wrapper))
), 

-- Part 1: Calculate positions with simple modulo wrapping
part1_positions AS (
    SELECT
        instruction_id,
        raw_instruction,
        direction,
        steps,
        
        -- Normalize direction: positive for R, negative for L
        if(direction = 'R', steps % 100, -1 * (steps % 100)) AS normalized_steps,
        
        -- Calculate cumulative position
        sum(normalized_steps) OVER (
            ORDER BY instruction_id
        ) AS raw_position,
        
        -- Wrap position to 0-99 range
        ((raw_position % 100) + 100) % 100 AS position
    FROM parsed_instructions
),

-- Part 2: Calculate positions with full movement tracking
position_calculations AS (
    SELECT
        instruction_id,
        raw_instruction,
        direction,
        steps,
        
        -- Normalize direction (no modulo yet)
        if(direction = 'R', steps, -1 * steps) AS normalized_steps,
        
        -- Calculate cumulative raw position
        sum(normalized_steps) OVER (
            ORDER BY instruction_id ASC
        ) AS raw_position,
        
        -- Wrap to 0-99 range
        ((raw_position % 100) + 100) % 100 AS position
    FROM parsed_instructions
),

-- Track turn counts based on position changes
turn_tracking AS (
    SELECT
        *,
        
        -- Get previous position for comparison
        lagInFrame(position) OVER (
            ORDER BY instruction_id ASC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS previous_position,
        
        -- Calculate turns for this instruction
        if(
            instruction_id = 0,
            0,
            
            -- Base turns from full rotations
            floor(steps / 100) + 
            
            -- Additional turn if we wrapped around
            if(
                direction = 'R',
                (position != 0 AND previous_position != 0 AND position < previous_position) ? 1 : 0,
                (position != 0 AND previous_position != 0 AND position > previous_position) ? 1 : 0
            )
        ) + 
        
        -- Extra turn if we land exactly on position 0
        if(instruction_id != 0 AND position = 0, 1, 0) AS turn_count
    FROM position_calculations
),

-- Calculate cumulative turn counts
part2_turn_counts AS (
    SELECT
        instruction_id,
        raw_instruction,
        direction,
        steps,
        position,
        turn_count,
        
        -- Running sum of turns
        sum(turn_count) OVER (
            ORDER BY instruction_id ASC 
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_turns
    FROM turn_tracking
)

-- Final results for both parts
SELECT 
    'Part 1' AS part,
    countIf(position = 0) AS solution -- Should be 1100 with my input
FROM part1_positions

UNION ALL

SELECT 
    'Part 2' AS part,
    max(cumulative_turns)::UInt64 AS solution -- Should be 6358 with my input
FROM part2_turn_counts;
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/1)

---

## Day 2: The Gift Shop

**The Puzzle**: You are helping clean up a gift shop database filled with invalid product IDs. The input is a list of ID ranges (e.g., 11-22, 95-115).

- **Part 1** defines an invalid ID as one composed of a sequence repeated exactly twice (like 1212 or 55).
- **Part 2** expands this to any sequence repeated _at least_ twice (like 123123123 or 11111). The goal is to sum up all invalid IDs found within the given ranges.

**How we solved this in ClickHouse SQL**: Instead of writing a loop to iterate through numbers, we leaned on ClickHouse's ability to "explode" data. We took the compact input ranges (like 11-22) and instantly expanded them into millions of individual rows - one for every integer in the range. Once we had a row for every potential ID, we converted them to strings and applied array functions to check for the repeating patterns in parallel.

**Implementation details**:

1. [`arrayJoin`](https://clickhouse.com/docs/en/sql-reference/functions/array-functions#arrayjoin): This function is our staple for generating rows. We used `range(start, end)` to create an array of integers for each input line, and `arrayJoin` to explode that array into separate rows. This made filtering for invalid IDs a simple `WHERE` clause operation.

```sql
SELECT arrayJoin(range(bounds[1], bounds[2] + 1)) AS number
```

2. [`arrayExists`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayExists): For Part 2, we had to check if any substring length (from 1 up to the string length) formed a repeating pattern. We used `arrayExists` with a lambda function to check every possible substring length. If the lambda returns 1 for any length, the ID is flagged.

```sql
arrayExists(
    x -> (string_length % x = 0) AND (repeat(substring(..., x), ...) = number_string),
    range(1, string_length)
)
```

**Full Solution:**


```sql
-- Define puzzle input
WITH input_wrapper AS (SELECT trimRight(raw_blob,'\n') AS input FROM aoc.input2),

-- Parse range bounds from input string
range_bounds AS (
    SELECT arrayMap(
        x -> x::UInt64,
        splitByChar('-', arrayJoin(splitByChar(',', (SELECT input FROM input_wrapper)::String)))
    ) AS bounds
),

-- Expand ranges into individual numbers
expanded_numbers AS (
    SELECT
        arrayJoin(range(bounds[1], bounds[2] + 1)) AS number,
        toString(number) AS number_string,
        length(number_string) AS string_length
    FROM range_bounds
),

-- Analyze each number for repeating patterns
repeating_analysis AS (
    SELECT
        number_string,
        toUInt64(number_string) AS number,
        
        -- Part 2: Check if string is made of any repeating pattern
        -- (e.g., "123123" = "123" repeated, "1111" = "1" repeated)
        arrayExists(
            x -> (string_length % x = 0)
                AND (
                    repeat(
                        substring(number_string, 1, x),
                        (string_length / x)::UInt32
                    ) = number_string
                ),
            range(1, string_length)
        ) AS has_pattern_repeat,
        
        -- Part 1: Check if second half equals first half
        -- (e.g., "1212" -> "12" = "12", "123123" -> "123" = "123")
        if(
            string_length % 2 = 0 
            AND substring(number_string, (string_length / 2) + 1, string_length / 2) 
                = substring(number_string, 1, string_length / 2),
            1,
            0
        ) AS has_half_repeat
    FROM expanded_numbers
    WHERE
        has_pattern_repeat != 0 
        OR has_half_repeat != 0
    ORDER BY number ASC
)

-- Calculate final solutions
SELECT 
    sumIf(number, has_half_repeat = 1) AS part_1_solution, -- Should be 24043483400 with my input
    sumIf(number, has_pattern_repeat = 1) AS part_2_solution -- Should be 38262920235 with my input
FROM repeating_analysis
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/2)

---

## Day 3: The Lobby

**The Puzzle**: You need to jumpstart an escalator using banks of batteries, where each bank is a string of digits (e.g., 987654321).

- **Part 1** asks you to pick exactly two batteries (digits) to form the largest possible 2-digit number, preserving their original relative order.
- **Part 2** scales this up: pick exactly 12 batteries to form the largest possible 12-digit number. This becomes a greedy optimization problem - you always want the largest available digit that still leaves enough digits after it to complete the sequence.

**How we solved this in ClickHouse SQL**: Part 1 was a straightforward string manipulation, but Part 2 required us to maintain state while iterating through the digits. We needed to track how many digits we still needed to find and our current position in the string so we wouldn't pick digits out of order. We implemented this greedy algorithm directly in SQL using `arrayFold`, which allowed us to iterate through the digits while carrying an accumulator tuple containing our current constraints.

**Implementation details**:

1. [`arrayFold`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayFold): We used this higher-order function to implement `reduce()`-style logic. Our accumulator stored a tuple: `(digits_remaining, current_position, accumulated_value)`. For every step of the fold, we calculated the best valid digit to pick next and updated the state tuple accordingly.

```sql
arrayFold(
    (accumulator, current_element) -> ( ... ), -- Update logic
    digits,
    (num_digits_needed, 0, 0) -- Initial state
)
```

2. [`ngrams`](https://clickhouse.com/docs/sql-reference/functions/splitting-merging-functions#ngrams): To process the string of digits as an array, we used `ngrams(string, 1)`. While typically used for text analysis, here it served as a convenient way to split a string into an array of single characters, which we then cast to integers for the `arrayFold` operation.

**Full Solution:**

```sql
-- Define puzzle input
WITH input_wrapper AS (SELECT trimBoth(raw_blob,'\n') AS input FROM aoc.input3),

-- Convert input to array of digit values for Part 2
digit_array AS (
    SELECT
        arrayMap(
            x -> toUInt8(x),
            ngrams(arrayJoin(splitByChar('\n', (SELECT input FROM input_wrapper)::String)), 1)
        ) AS digits,
        length(digits) AS total_digits
),

-- Constants
12 AS num_digits_needed,

-- Part 1: Find largest two-digit number from each line
part1_largest_pairs AS (
    SELECT
        ngrams(arrayJoin(splitByChar('\n', (SELECT input FROM input_wrapper)::String)), 1) AS chars,
        arraySlice(chars, 1, length(chars) - 1) AS chars_without_last,
        
        -- Find first max digit, then find max digit after it
        concat(
            arrayMax(chars_without_last),
            arrayMax(
                arraySlice(
                    chars,
                    arrayFirstIndex(
                        x -> x = arrayMax(chars_without_last),
                        chars
                    ) + 1
                )
            )
        )::Int16 AS largest_two_digit
),

-- Part 2: Build largest N-digit number by greedily selecting max digits
part2_greedy_selection AS (
    SELECT
        digits,
        
        -- Iteratively build number by selecting maximum available digit
        arrayFold(
            (accumulator, current_element) -> (
                -- Decrement remaining digits counter
                greatest(accumulator.1 - 1, 0)::Int64,
                
                -- Update position: find where max digit is in remaining slice
                accumulator.2 + (
                    arrayFirstIndex(
                        x -> x = arrayMax(
                            arraySlice(
                                digits,
                                accumulator.2 + 1,
                                total_digits - accumulator.1 - accumulator.2 + 1
                            )
                        ),
                        arraySlice(
                            digits,
                            accumulator.2 + 1,
                            total_digits - accumulator.1 - accumulator.2 + 1
                        )
                    )
                )::UInt64,
                
                -- Accumulate joltage: add max digit * 10^(remaining-1)
                accumulator.3 + if(
                    accumulator.1 = 0,
                    0::UInt64,
                    arrayMax(
                        arraySlice(
                            digits,
                            accumulator.2 + 1,
                            total_digits - accumulator.1 - accumulator.2 + 1
                        )
                    ) * intExp10(greatest(0, accumulator.1 - 1))
                )
            ),
            digits,
            
            -- Initial accumulator state:
            -- (digits_remaining, current_position, accumulated_value)
            (num_digits_needed::Int64, 0::UInt64, 0::UInt64)
        ).3 AS joltage  -- Extract the accumulated value (3rd element)
    
    FROM digit_array
)

-- Combine results from both parts
SELECT
    'Part 1' AS part,
    sum(largest_two_digit)::UInt64 AS solution -- Should be 17263 with my input
FROM part1_largest_pairs

UNION ALL

SELECT
    'Part 2' AS part,
    sum(joltage) AS solution -- Should be 170731717900423 with my input
FROM part2_greedy_selection
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/3)

---

## Day 4: The Printing Department

**The Puzzle**: The elves need to break through a wall of paper rolls. The puzzle is a variation of Conway's Game of Life. You are given a grid where `@` represents a roll of paper.

- **Part 1** defines a rule: a roll can be "accessed" (removed) if it has fewer than 4 neighbors. You count how many rolls fit this criteria initially.
- **Part 2** asks to simulate this process recursively. Removing a roll might open up access to others. You need to keep removing accessible rolls until the system stabilizes, then count the total removed.

**How we solved this in ClickHouse SQL**: Since this problem required iterative simulation where each step depended on the previous one, we used a Recursive CTE. We represented the grid as a set of (x, y) coordinates. In each recursive step, we performed a self-join to count the neighbors for every point. We filtered the list to keep only the points that "survived" (had >= 4 neighbors), implicitly removing the others. We continued this recursion until the count of points stopped changing.

**Implementation details**:

1. [`WITH RECURSIVE`](https://clickhouse.com/docs/sql-reference/statements/select/with#recursive-queries): We used the standard SQL recursive CTE to handle the graph traversal. The base case selected all initial paper roll positions. The recursive step filtered that set down based on neighbor counts.

```sql
WITH RECURSIVE recursive_convergence AS (
    -- Base case: all points
    UNION ALL
    -- Recursive step: keep points with >= 4 neighbors
    SELECT ... HAVING countIf(...) >= 4
)
```

2. [`argMin`](https://clickhouse.com/docs/en/sql-reference/aggregate-functions/reference/argmin): To find the exact moment the simulation stabilized, we tracked the point count at every depth of the recursion. We used `argMin(point_count, depth)` to retrieve the count of remaining points exactly at the minimum depth where the count stopped changing.

**Full Solution:**

```sql
WITH RECURSIVE 
-- Define puzzle input (grid with '@' symbols)
input_wrapper AS (SELECT raw_blob AS input FROM aoc.input4),

-- Split input into lines
input_lines AS (
    SELECT splitByChar('\n', (SELECT input FROM input_wrapper)::String) AS lines
),

-- Find all '@' symbol positions in the grid
grid_points AS (
    SELECT arrayJoin(
        arrayFlatten(
            arrayMap(
                line_tuple -> 
                    arrayMap(
                        x_pos -> (x_pos, line_tuple.2),
                        arrayFilter(
                            (pos, val) -> val = '@',
                            arrayEnumerate(line_tuple.1),
                            line_tuple.1
                        )
                    ),
                arrayMap(
                    (line, line_num) -> (ngrams(line, 1), line_num),
                    lines,
                    range(1, length(lines) + 1)
                )
            )
        )::Array(Tuple(UInt8, UInt8))
    ) AS point
    FROM input_lines
),

-- Expand points into separate columns
initial_points AS (
    SELECT 
        point.1 AS x,
        point.2 AS y
    FROM grid_points
),

-- Recursive CTE: Keep only points with 4+ neighbors at each iteration
recursive_convergence AS (
    -- Base case: all initial points at depth 1
    SELECT
        x,
        y,
        1 AS depth
    FROM initial_points

    UNION ALL

    -- Recursive case: keep points with at least 4 neighbors
    SELECT
        p.x,
        p.y,
        depth + 1 AS depth
    FROM recursive_convergence AS p
    CROSS JOIN recursive_convergence AS q
    WHERE depth < 256  -- Maximum recursion depth
    GROUP BY p.x, p.y, depth
    HAVING countIf(
        q.x BETWEEN p.x - 1 AND p.x + 1
        AND q.y BETWEEN p.y - 1 AND p.y + 1
        AND NOT (p.x = q.x AND p.y = q.y)
    ) >= 4
),

-- Track point counts at each depth level
depth_statistics AS (
    SELECT 
        depth,
        count() AS point_count,
        lagInFrame(point_count, 1) OVER (ORDER BY depth) AS previous_count
    FROM recursive_convergence
    GROUP BY depth
    ORDER BY depth
),

-- Find the depth where the count stabilizes (no more points removed)
stabilization_analysis AS (
    SELECT 
        min(depth) AS stabilization_depth,
        argMin(point_count, depth) AS stabilized_count
    FROM depth_statistics
    WHERE point_count = previous_count 
        AND point_count > 0
),

-- Part 1: Points removed after first iteration (depth 2)
part1_solution AS (
    SELECT
        (SELECT count() FROM initial_points) - 
        (SELECT point_count FROM depth_statistics WHERE depth = 2 LIMIT 1) AS solution
),

-- Part 2: Points removed when convergence stabilizes
part2_solution AS (
    SELECT
        (SELECT count() FROM initial_points) - stabilized_count AS solution
    FROM stabilization_analysis
),

-- Combine results from both parts (necessary to prevent a bug with recursive CTE/external UNIONs)
combined_solutions AS (
SELECT
    'Part 1' AS part,
    solution -- Should be 1604 with my input
FROM part1_solution

UNION ALL

SELECT
    'Part 2' AS part,
    solution -- Should be 9397 with my input
FROM part2_solution)

select * from combined_solutions settings use_query_cache=true, query_cache_share_between_users = 1, query_cache_nondeterministic_function_handling = 'save', query_cache_ttl = 80000000, result_overflow_mode = 'throw', read_overflow_mode = 'throw'
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/4)

---

## Day 5: The Cafeteria

**The Puzzle**: The elves have an inventory problem involving lists of "fresh" ID ranges (e.g., 3-5, 10-14).

- **Part 1** asks how many specific item IDs fall into any of the fresh ranges.
- **Part 2** asks for the total count of unique integers covered by the fresh ranges (the union of all intervals). For example, if you have ranges 1-5 and 3-7, the union is 1-7 (size 7), not 1-5 + 3-7 (size 10).

**How we solved this in ClickHouse SQL**: This is a classic interval intersection problem. While Part 1 was a simple filter, Part 2 required merging overlapping intervals. Merging intervals can be mathematically complex to implement manually, but we utilized a specialized ClickHouse aggregation function designed exactly for this purpose, turning a complex geometric algorithm into a one-liner.

**Implementation details**:

1. [`intervalLengthSum`](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/intervallengthsum): We used this specialized aggregate function to calculate the total length of the union of intervals. It automatically handles overlapping and nested ranges, saving us from writing complex merging logic.

```sql
SELECT intervalLengthSum(range_tuple.1, range_tuple.2) AS solution
```

2. [`arrayExists`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayExists): For Part 1, we used arrayExists to check if a specific ID fell within _any_ of the valid ranges in the array. This allowed us to perform the check efficiently without exploding the ranges into billions of individual rows.

**Full Solution:**

```sql
-- Define puzzle input
WITH input_wrapper AS (SELECT trimRight(raw_blob,'\n') AS input FROM aoc.input5),

-- Split input into two sections
input_sections AS (
    SELECT
        splitByString('\n\n', (SELECT input FROM input_wrapper)::String)[1] AS ranges_section,
        splitByString('\n\n', (SELECT input FROM input_wrapper)::String)[2] AS ids_section
),

-- Parse ranges from first section (format: "min-max" per line)
parsed_ranges AS (
    SELECT arrayMap(
        x -> (
            toUInt64(splitByChar('-', x)[1]),
            toUInt64(splitByChar('-', x)[2]) + 1 -- Make max half-open
        ),
        splitByChar('\n', ranges_section)
    ) AS ranges
    FROM input_sections
),

-- Parse IDs from second section (one ID per line)
parsed_ids AS (
    SELECT arrayMap(
        x -> toUInt64(x),
        splitByChar('\n', ids_section)
    ) AS ids
    FROM input_sections
),

-- Explode ranges into individual rows for Part 2 interval calculation
exploded_ranges AS (
    SELECT arrayJoin(ranges) AS range_tuple
    FROM parsed_ranges
),

-- Part 1: Count how many IDs fall within any range
part1_solution AS (
    SELECT
        length(
            arrayFilter(
                id -> arrayExists(
                    range -> id BETWEEN range.1 AND range.2,
                    ranges
                ),
                ids
            )
        ) AS solution
    FROM parsed_ranges, parsed_ids
),

-- Part 2: Calculate total interval length (union of all ranges)
part2_solution AS (
    SELECT
        intervalLengthSum(range_tuple.1, range_tuple.2) AS solution
    FROM exploded_ranges
)

-- Combine results from both parts
SELECT
    'Part 1' AS part,
    solution -- Should be 707 with my input
FROM part1_solution

UNION ALL

SELECT
    'Part 2' AS part,
    solution -- Should be 361615643045059 with my input
FROM part2_solution;
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/5)

---

## Day 6: The Trash Compactor

**The Puzzle**: You find a math worksheet with problems arranged in columns.

- **Part 1** interprets the input as columns of numbers separated by spaces. You need to sum or multiply the numbers in each column based on the operator at the bottom.
- **Part 2** reveals the input is written "right-to-left" in columns, where digits of a single number are stacked vertically. You must re-parse the grid to reconstruct the numbers, group them by blank columns, and apply the operators.

**How we solved this in ClickHouse SQL**: This puzzle was all about parsing and array manipulation. We treated the input text as a 2D matrix of characters. To switch from the row-based text file to the column-based math problems, we essentially performed a "matrix transposition." We converted the rows of text into arrays of characters, "rotated" them to process columns, and then used array functions to reconstruct the numbers and apply the math operations.

**Implementation details**:

1. [`splitByWhitespace`](https://clickhouse.com/docs/sql-reference/functions/splitting-merging-functions#splitByWhitespace): In Part 1, we used this function to parse the "horizontal" representation. It automatically handled the variable spacing between columns, which would have tripped up simple string splitting.

2. [`arrayProduct`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayProduct): Since ClickHouse lacks a standard `product()` aggregate function, we mapped our columns to arrays of integers and used `arrayProduct` to calculate the multiplication results.

```sql
toInt64(arrayProduct(
    arrayMap(x -> toInt64(x), arraySlice(column, 1, length(column) - 1))
))
```

3. [`arraySplit`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arraySplit): For Part 2, after extracting the raw digits, we needed to group them into valid expressions. We used `arraySplit` to break the large array into chunks whenever we encountered an operator column, effectively separating the mathematical problems.

**Full Solution:**


```sql
-- Define puzzle input
WITH input_wrapper AS (SELECT trimRight(raw_blob,'\n') AS input FROM aoc.input6),

-- Part 1: Parse input into columns and apply operations
part1_parsed_rows AS (
    SELECT arrayMap(
        x -> splitByWhitespace(x),
        splitByChar('\n', (SELECT input FROM input_wrapper)::String)
    ) AS rows
),

part1_columns AS (
    SELECT arrayMap(
        column_index -> arrayMap(
            row -> row[column_index],
            rows
        ),
        range(1, length(rows[1]) + 1)
    ) AS columns
    FROM part1_parsed_rows
),

part1_solution AS (
    SELECT arraySum(
        arrayMap(
            column -> if(
                -- Check if last element is multiplication operator
                arrayLast(x -> 1, column) = '*',
                
                -- Multiply all numbers in column
                toInt64(arrayProduct(
                    arrayMap(
                        x -> toInt64(x),
                        arraySlice(column, 1, length(column) - 1)
                    )
                )),
                
                -- Otherwise, add all numbers in column
                toInt64(arraySum(
                    arrayMap(
                        x -> toInt64(x),
                        arraySlice(column, 1, length(column) - 1)
                    )
                ))
            ),
            columns
        )
    ) AS solution
    FROM part1_columns
),

-- Part 2: Parse with character-level precision to handle multi-digit numbers
part2_parsed_chars AS (
    SELECT arrayMap(
        x -> ngrams(x, 1),
        splitByChar('\n', (SELECT input FROM input_wrapper)::String)
    ) AS char_rows
),

part2_columns_raw AS (
    SELECT arrayMap(
        column_index -> arrayMap(
            row -> row[column_index],
            char_rows
        ),
        range(1, length(char_rows[1]) + 1)
    ) AS columns
    FROM part2_parsed_chars
),

part2_columns_filtered AS (
    SELECT arrayFilter(
        x -> NOT arrayAll(y -> y = ' ', x),
        columns
    ) AS non_empty_columns
    FROM part2_columns_raw
),

part2_numbers_extracted AS (
    SELECT arrayMap(
        column -> replaceAll(
            arrayStringConcat(
                arraySlice(column, 1, length(column) - 1)
            ),
            ' ',
            ''
        ),
        non_empty_columns
    ) AS number_strings
    FROM part2_columns_filtered
),

part2_numbers_grouped AS (
    SELECT
        number_strings,
        non_empty_columns,
        
        -- Split numbers by operator positions
        arraySplit(
            (number_str, has_operator) -> has_operator,
            number_strings,
            arrayMap(
                column -> hasAny(column, ['+', '*']),
                non_empty_columns
            )
        ) AS number_groups
    FROM part2_numbers_extracted, part2_columns_filtered
),

part2_operations AS (
    SELECT arrayZip(
        -- Extract operators from columns
        arrayFilter(
            x -> has(['+', '*'], x),
            arrayFlatten(non_empty_columns)
        ),
        -- Pair with corresponding number groups
        number_groups
    ) AS operations_with_numbers
    FROM part2_numbers_grouped
),

part2_solution AS (
    SELECT arraySum(
        arrayMap(
            operation -> if(
                -- Check operator type
                operation.1 = '*',
                
                -- Multiply all numbers in group
                toInt64(arrayProduct(
                    arrayMap(
                        x -> toInt64(x),
                        operation.2
                    )
                )),
                
                -- Otherwise, add all numbers in group
                toInt64(arraySum(
                    arrayMap(
                        x -> toInt64(x),
                        operation.2
                    )
                ))
            ),
            operations_with_numbers
        )
    ) AS solution
    FROM part2_operations
)

-- Combine results from both parts
SELECT
    'Part 1' AS part,
    solution -- 5782351442566 with my input
FROM part1_solution

UNION ALL

SELECT
    'Part 2' AS part,
    solution -- 10194584711842 with my input
FROM part2_solution;
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/6)

---

## Day 7: The Teleporter Lab

**The Puzzle**: You are analyzing a tachyon beam in a grid.

- **Part 1** simulates a beam moving downwards. When it hits a splitter `^`, it splits into two beams (left and right). You count the total splits.
- **Part 2** introduces a "quantum many-worlds" twist: instead of splitting the beam, the universe splits. You need to calculate the total number of active "timelines" (paths) at the bottom of the grid.

**How we solved this in ClickHouse SQL**: Simulating individual paths would have caused an exponential explosion. Instead, we approached this like a wave propagation simulation (similar to calculating Pascal's triangle). We processed the grid row-by-row using `arrayFold`. For each row, we maintained a map of "active world counts" at each column position and calculated how the counts flowed into the next row based on the splitters.

**Implementation details**:

1. [`arrayFold`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayFold): We used `arrayFold` to implement the row-by-row simulation state machine. We carried a complex state object - `(left_boundary, right_boundary, worlds_map, part1_counter)` - and updated it for each row of the grid.

2. [`sumMap`](https://clickhouse.com/docs/sql-reference/aggregate-functions/reference/summap): To handle beams merging (e.g., a left branch and a right branch meeting at the same spot), we used `sumMap`. This allowed us to aggregate values for identical keys in our world map, easily combining the counts of "timelines" converging on a single coordinate. 

```sql
arrayReduce('sumMap', arrayMap(position -> map(...), ...))
```

**Full Solution:**

```sql
-- Define puzzle input 
WITH input_wrapper AS (SELECT raw_blob AS input FROM aoc.input7),

-- Parse input into character grid
parsed_grid AS (
    SELECT arrayMap(
        x -> ngrams(x, 1),
        splitByChar('\n', (SELECT input FROM input_wrapper)::String)
    ) AS rows
),

-- Find starting position in first row
initial_state AS (
    SELECT
        arrayFirstIndex(x -> x = 'S', rows[1])::UInt8 AS start_position,
        map(
            arrayFirstIndex(x -> x = 'S', rows[1])::UInt8,
            1::UInt64
        )::Map(UInt8, UInt64) AS initial_worlds
    FROM parsed_grid
),

-- Filter to only rows with '^' markers (active rows)
active_rows AS (
    SELECT arrayFilter(
        x -> has(x, '^'),
        rows
    ) AS filtered_rows
    FROM parsed_grid
),

-- Main iteration: propagate world counts through rows
world_propagation AS (
    SELECT
        start_position,
        initial_worlds,
        filtered_rows,
        
        -- Fold through each row, updating state
        arrayFold(
            (accumulator, current_row) -> (
                -- Update left boundary (shrink inward)
                (accumulator.1 - 1)::UInt8,
                
                -- Update right boundary (shrink inward)
                (accumulator.2 + 1)::UInt8,
                
                -- Update world map: propagate counts based on '^' positions
                mapSort(
                    (key, value) -> key,
                    mapUpdate(
                        accumulator.3,
                        arrayReduce(
                            'sumMap',
                            arrayMap(
                                position -> if(
                                    -- Check if position has '^' and exists in current worlds
                                    current_row[position] = '^'
                                    AND mapContains(accumulator.3, position),
                                    
                                    -- Propagate world count to adjacent positions
                                    map(
                                        -- Left neighbor gets count (unless blocked by another '^')
                                        (position - 1)::UInt8,
                                        (
                                            accumulator.3[position] + if(
                                                current_row[greatest(0, position - 2)] = '^',
                                                0,
                                                accumulator.3[position - 1]
                                            )
                                        )::UInt64,
                                        
                                        -- Current position resets to 0
                                        (position)::UInt8,
                                        0::UInt64,
                                        
                                        -- Right neighbor gets count
                                        (position + 1)::UInt8,
                                        (accumulator.3[position + 1] + accumulator.3[position])::UInt64
                                    ),
                                    
                                    -- No propagation if conditions not met
                                    map()::Map(UInt8, UInt64)
                                ),
                                -- Only process positions within current boundaries
                                arraySlice(
                                    arrayEnumerate(current_row),
                                    accumulator.1,
                                    (accumulator.2 - accumulator.1) + 1
                                )
                            )
                        )
                    )
                ),
                
                -- Part 1 counter: count '^' positions with non-zero worlds
                accumulator.4 + arrayCount(
                    position -> 
                        current_row[position] = '^'
                        AND mapContains(accumulator.3, position)
                        AND accumulator.3[position] > 0,
                    arraySlice(
                        arrayEnumerate(current_row),
                        accumulator.1,
                        (accumulator.2 - accumulator.1) + 1
                    )
                )
            ),
            filtered_rows,
            
            -- Initial accumulator state:
            -- (left_boundary, right_boundary, worlds_map, part1_counter)
            (
                start_position,
                start_position,
                initial_worlds,
                0::UInt64
            )
        ) AS final_state
    FROM initial_state, active_rows
),

-- Part 1: Count of '^' positions encountered with non-zero worlds
part1_solution AS (
    SELECT final_state.4 AS solution
    FROM world_propagation
),

-- Part 2: Sum of all world counts across all positions
part2_solution AS (
    SELECT arraySum(mapValues(final_state.3)) AS solution
    FROM world_propagation
)

-- Combine results from both parts
SELECT
    'Part 1' AS part,
    solution -- 1633 with my input
FROM part1_solution

UNION ALL

SELECT
    'Part 2' AS part,
    solution -- 34339203133559 with my input
FROM part2_solution;
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/7)

---

## Day 8: The Playground

**The Puzzle**: The elves are connecting 3D electrical junction boxes.

- **Part 1** asks to connect the 1000 closest pairs of points and analyze the resulting circuit sizes (connected components).
- **Part 2** asks to keep connecting the closest points until _all_ boxes form a single giant circuit (a Minimum Spanning Tree problem).

**How we solved this in ClickHouse SQL**: This is a graph theory problem requiring a disjoint-set (union-find) approach. We generated all possible edges between points and sorted them by distance. Then, we used `arrayFold` to iterate through the edges, merging sets of points into connected components whenever an edge bridged two previously separate groups.

**Implementation details**:

1. [`L2Distance`](https://clickhouse.com/docs/sql-reference/functions/distance-functions#L2Distance): We used ClickHouse's native `L2Distance` function to efficiently calculate the Euclidean distance between 3D coordinates `[x, y, z]`, allowing us to sort the potential connections by length.

2. [`runningAccumulate`](https://clickhouse.com/docs/sql-reference/functions/other-functions#runningAccumulate): For Part 2, we needed to know when we had seen enough unique points to form a single circuit. Instead of running a slow `DISTINCT` count on every row, we used `uniqCombinedState` to create a compact sketch of unique elements, and `runningAccumulate` to merge these sketches row-by-row, providing a running count of unique points efficiently.

```sql
runningAccumulate(points_state) AS unique_points_seen
```

**Full Solution:**

```sql
-- Define puzzle input 
WITH input_wrapper AS (SELECT raw_blob AS input FROM aoc.input8),

-- Parse 3D coordinate points
parsed_points AS (
    SELECT (x, y, z) AS point
    FROM format('CSV', 'x UInt32, y UInt32, z UInt32', (SELECT input FROM input_wrapper)::String)
),

-- Generate all point pairs with L2 distances, sorted by distance
point_pairs_by_distance AS (
    SELECT
        t1.point AS point1,
        t2.point AS point2,
        L2Distance(
            [point1.1, point1.2, point1.3],
            [point2.1, point2.2, point2.3]
        ) AS distance
    FROM parsed_points AS t1
    CROSS JOIN parsed_points AS t2
    WHERE point1 < point2
    ORDER BY distance ASC
),

-- Take the 1000 closest pairs
closest_pairs AS (
    SELECT groupArray([point1, point2]) AS pairs
    FROM (
        SELECT point1, point2
        FROM point_pairs_by_distance
        ORDER BY distance ASC
        LIMIT 1000
    )
),

-- Part 1: Build connected components from closest pairs
connected_components AS (
    SELECT
        pairs,
        
        -- Fold through pairs to merge into connected components
        arrayFold(
            (accumulator, pair) -> if(
                -- Check if any existing components contain points from current pair
                length(
                    arrayFilter(
                        component -> hasAny(component, pair),
                        accumulator
                    )
                ) > 0,
                
                -- Merge matching components with current pair
                arrayConcat(
                    -- Keep non-matching components unchanged
                    arrayFilter(
                        component -> NOT hasAny(component, pair),
                        accumulator
                    ),
                    -- Add merged component
                    [
                        arrayDistinct(
                            arrayFlatten(
                                arrayConcat(
                                    arrayFilter(
                                        component -> hasAny(component, pair),
                                        accumulator
                                    ),
                                    [pair]
                                )
                            )
                        )
                    ]
                ),
                
                -- No matches found, add pair as new component
                arrayConcat(accumulator, [pair])
            ),
            pairs,
            []::Array(Array(Tuple(UInt32, UInt32, UInt32)))
        ) AS components
    FROM closest_pairs
),

component_analysis AS (
    SELECT
        components,
        arrayMap(x -> length(x), components) AS component_sizes
    FROM connected_components
),

part1_solution AS (
    SELECT arrayProduct(
        arraySlice(
            arrayReverseSort(component_sizes),
            1,
            3
        )
    ) AS solution
    FROM component_analysis
),

-- Part 2: Find first pair where 1000 unique points have been seen
point_pair_states AS (
    SELECT
        point1,
        point2,
        distance,
        arrayReduce('uniqCombinedState', [point1, point2]) AS points_state
    FROM point_pairs_by_distance
),

part2_solution AS (
    SELECT
        point1,
        point2,
        distance,
        runningAccumulate(points_state) AS unique_points_seen,
        point1.1 * point2.1 AS solution
    FROM point_pair_states
    WHERE unique_points_seen >= 1000
    ORDER BY distance ASC
    LIMIT 1
)

-- Combine results from both parts
SELECT
    'Part 1' AS part,
    solution::UInt64 AS solution -- 135169 with my input
FROM part1_solution

UNION ALL

SELECT
    'Part 2' AS part,
    solution::UInt64 AS solution -- 302133440 with my input
FROM part2_solution

SETTINGS allow_deprecated_error_prone_window_functions = 1;
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/8)

---

## Day 9: The Movie Theater

**The Puzzle**: The theater floor is a grid with some red tiles.

- **Part 1** asks for the largest area rectangle formed using two red tiles as opposite corners.
- **Part 2** adds a constraint: the rectangle must fit entirely inside the loop formed by all the red/green tiles.

**How we solved this in ClickHouse SQL**: We treated this as a geometry problem rather than a grid search. We constructed polygons representing the candidate rectangles and the boundary loop. By converting the bounding boxes into "rings," we could use ClickHouse's native geometry functions to calculate areas and check for containment.

**Implementation details**:

1. [`polygonAreaCartesian`](https://clickhouse.com/docs/sql-reference/functions/geo/polygons#polygonareacartesian): We avoided manual width/height calculations by constructing polygon objects for our rectangles and using `polygonAreaCartesian` to compute their area directly.

2. [`polygonsWithinCartesian`](https://clickhouse.com/docs/sql-reference/functions/geo/polygons#polygonswithincartesian): To check if a rectangle fit inside the loop, we used this containment function. We applied a clever trick here: because geometric functions can be tricky about points shared exactly on an edge, we constructed a slightly **inset** version of the candidate rectangle (shrunk by 0.01 units). This ensured the containment check strictly validated that the rectangle fit _inside_ the boundary polygon without edge alignment errors.

```sql
-- Create slightly inset test bounds (0.01 units inside)
(least(x1, x2) + 0.01, least(y1, y2) + 0.01) AS bottom_left, ...
polygonsWithinCartesian(test_bounds, all_points_ring)
```

**Full Solution:**

```sql
-- Define puzzle input 
WITH input_wrapper AS (SELECT raw_blob AS input FROM aoc.input9),

-- Parse 2D coordinate points
parsed_points AS (
    SELECT *
    FROM format('CSV', 'x Float64, y Float64', (SELECT input FROM input_wrapper)::String)
),

-- Generate all unique pairs of points
point_pairs AS (
    SELECT
        c1.x AS x1,
        c1.y AS y1,
        c2.x AS x2,
        c2.y AS y2
    FROM parsed_points AS c1
    CROSS JOIN parsed_points AS c2
    WHERE (c1.x, c1.y) < (c2.x, c2.y)
),

-- Create bounding box polygons for each pair
bounding_boxes AS (
    SELECT
        x1,
        y1,
        x2,
        y2,
        
        -- Exact bounding box (corners at point coordinates)
        [
            (least(x1, x2), least(y1, y2)),        -- bottom-left
            (least(x1, x2), greatest(y1, y2)),     -- top-left
            (greatest(x1, x2), greatest(y1, y2)),  -- top-right
            (greatest(x1, x2), least(y1, y2)),     -- bottom-right
            (least(x1, x2), least(y1, y2))         -- close the ring
        ]::Ring AS exact_bounds,
        
        -- Expanded bounding box (extends 0.5 units beyond points)
        [
            (least(x1, x2) - 0.5, least(y1, y2) - 0.5),        -- bottom-left
            (least(x1, x2) - 0.5, greatest(y1, y2) + 0.5),     -- top-left
            (greatest(x1, x2) + 0.5, greatest(y1, y2) + 0.5),  -- top-right
            (greatest(x1, x2) + 0.5, least(y1, y2) - 0.5),     -- bottom-right
            (least(x1, x2) - 0.5, least(y1, y2) - 0.5)         -- close the ring
        ]::Ring AS expanded_bounds
    FROM point_pairs
),

-- Create polygon containing all points (for Part 2 containment test)
all_points_array AS (
    SELECT groupArray((x, y)) AS points_array
    FROM parsed_points
),

all_points_polygon AS (
    SELECT arrayPushBack(points_array, points_array[1])::Ring AS ring
    FROM all_points_array
),

-- Part 1: Find largest bounding box by area
part1_candidates AS (
    SELECT
        x1,
        y1,
        x2,
        y2,
        exact_bounds,
        expanded_bounds,
        polygonAreaCartesian(expanded_bounds) AS area
    FROM bounding_boxes
    ORDER BY area DESC
    LIMIT 1
),

part1_solution AS (
    SELECT area AS solution
    FROM part1_candidates
),

-- Part 2: Find largest bounding box that contains all points
part2_candidates AS (
    SELECT
        bb.x1,
        bb.y1,
        bb.x2,
        bb.y2,
        
        -- Create slightly inset test bounds (0.01 units inside)
        (least(x1, x2) + 0.01, least(y1, y2) + 0.01) AS bottom_left,
        (least(x1, x2) + 0.01, greatest(y1, y2) - 0.01) AS top_left,
        (greatest(x1, x2) - 0.01, greatest(y1, y2) - 0.01) AS top_right,
        (greatest(x1, x2) - 0.01, least(y1, y2) + 0.01) AS bottom_right,
        
        -- Create test bounds polygon
        [
            bottom_left,
            top_left,
            top_right,
            bottom_right,
            bottom_left
        ]::Ring AS test_bounds,
        
        -- Check if all points are within test bounds
        polygonsWithinCartesian(test_bounds, app.ring) AS all_points_contained,
        
        polygonAreaCartesian(bb.expanded_bounds) AS area
    FROM bounding_boxes AS bb
    CROSS JOIN all_points_polygon AS app
    WHERE all_points_contained != 0
    ORDER BY area DESC
    LIMIT 1
),

part2_solution AS (
    SELECT area AS solution
    FROM part2_candidates
)

-- Combine results from both parts
SELECT
    'Part 1' AS part,
    solution AS area -- 4739623064 with my input
FROM part1_solution

UNION ALL

SELECT
    'Part 2' AS part,
    solution AS area -- 1654141440 with my input
FROM part2_solution;
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/9)

---

## Day 10: The Factory

**The Puzzle**: You need to configure factory machines by pressing buttons.

- **Part 1** involves toggling lights (XOR logic) to match a pattern.
- **Part 2** involves incrementing "joltage" counters to reach large target integers using the fewest button presses.

**How we solved this in ClickHouse SQL**: For Part 1, the search space was small enough that we could use brute-force enumeration. We generated every possible button combination and checked it using bitmasks. Part 2 required a smarter approach. We implemented a custom recursive halving algorithm in SQL. We iteratively subtracted button effects and "halved" the remaining target values, reducing the large target numbers down to zero step-by-step.

**Implementation details**:

1. [`bitTest`](https://clickhouse.com/docs/sql-reference/functions/bit-functions#bitTest) and [`bitCount`](https://clickhouse.com/docs/sql-reference/functions/bit-functions#bitCount): We treated button combinations as binary integers. `bitTest` allowed us to check if a specific button was pressed in a combination, and `bitCount` gave us the total number of presses (the cost).

2. [`ARRAY JOIN`](https://clickhouse.com/docs/en/sql-reference/statements/select/array-join): To generate the search space for Part 1, we created a range of integers (0 to 2^N) and used `ARRAY JOIN` to explode them into rows. This created a row for every possible permutation of button presses.

```sql
ARRAY JOIN range(0, toUInt32(pow(2, num_buttons)))
```

**Full Solution:**

```sql
WITH RECURSIVE
-- Define puzzle input 
    input_wrapper AS (SELECT raw_blob AS input FROM aoc.input10),

-- Parse raw input into structured format
raw_split AS (
    SELECT
        row_number() OVER () AS puzzle_id,
        splitByChar(' ', raw) AS components
    FROM format('TSVRaw', 'raw String', (SELECT input FROM input_wrapper)::String)
),

parsed_puzzles AS (
    SELECT
        puzzle_id,
        
        -- Parse diagram: '#' becomes 1, '.' becomes 0
        arrayMap(
            x -> if(x = '#', 1, 0),
            ngrams(replaceRegexpAll(components[1], '[\\[\\]]', ''), 1)
        ) AS target_diagram,
        
        -- Parse buttons: each button affects specific positions
        arrayMap(
            button_str -> arrayMap(
                pos_str -> (toUInt16(pos_str) + 1),
                splitByChar(',', replaceRegexpAll(button_str, '[\\(\\)]', ''))
            ),
            arraySlice(components, 2, length(components) - 2)
        ) AS button_effects,
        
        -- Parse joltages: target values for Part 2
        arrayMap(
            x -> toUInt32(x),
            splitByChar(',', replaceRegexpAll(components[-1], '[\\{\\}]', ''))
        ) AS target_joltages
    FROM raw_split
),

puzzle_metadata AS (
    SELECT
        puzzle_id,
        target_diagram,
        button_effects,
        target_joltages,
        length(button_effects) AS num_buttons,
        length(target_joltages) AS num_positions
    FROM parsed_puzzles
),

-- PART 1: Brute force - enumerate all button combinations
part1_button_combinations AS (
    SELECT
        p.puzzle_id,
        p.target_diagram,
        p.button_effects,
        p.num_buttons,
        p.num_positions,
        combination_id,
        toUInt32(bitCount(combination_id)) AS button_presses,
        
        -- Calculate resulting diagram from this combination
        arrayMap(
            position -> toUInt8(
                modulo(
                    arrayReduce(
                        'sum',
                        arrayMap(
                            button_index -> if(
                                bitTest(combination_id, button_index)
                                AND has(button_effects[button_index + 1], position),
                                1,
                                0
                            ),
                            range(0, num_buttons)
                        )
                    ),
                    2
                )
            ),
            range(1, num_positions + 1)
        ) AS resulting_diagram
    FROM puzzle_metadata p
    ARRAY JOIN range(0, toUInt32(pow(2, num_buttons))) AS combination_id
),

part1_minimum_solutions AS (
    SELECT
        puzzle_id,
        min(button_presses) AS minimum_presses
    FROM part1_button_combinations
    WHERE target_diagram = resulting_diagram
    GROUP BY puzzle_id
),

-- PART 2: Pre-compute button combination patterns for recursive algorithm
button_combination_patterns AS (
    SELECT
        p.puzzle_id,
        p.button_effects,
        p.num_buttons,
        p.num_positions,
        combination_id,
        toUInt32(bitCount(combination_id)) AS pattern_cost,
        
        -- Pattern: numeric effect on each position
        arrayMap(
            position -> toUInt32(
                arrayReduce(
                    'sum',
                    arrayMap(
                        button_index -> if(
                            bitTest(combination_id, button_index)
                            AND has(button_effects[button_index + 1], position),
                            1,
                            0
                        ),
                        range(0, num_buttons)
                    )
                )
            ),
            range(1, num_positions + 1)
        ) AS effect_pattern,
        
        -- Parity pattern: XOR constraint (mod 2)
        arrayMap(
            position -> toUInt8(
                modulo(
                    arrayReduce(
                        'sum',
                        arrayMap(
                            button_index -> if(
                                bitTest(combination_id, button_index)
                                AND has(button_effects[button_index + 1], position),
                                1,
                                0
                            ),
                            range(0, num_buttons)
                        )
                    ),
                    2
                )
            ),
            range(1, num_positions + 1)
        ) AS parity_pattern
    FROM puzzle_metadata p
    ARRAY JOIN range(0, toUInt32(pow(2, num_buttons))) AS combination_id
),

-- Group patterns by parity for efficient lookup
patterns_grouped_by_parity AS (
    SELECT
        puzzle_id,
        button_effects,
        num_buttons,
        num_positions,
        parity_pattern,
        groupArray(tuple(effect_pattern, pattern_cost)) AS available_patterns
    FROM button_combination_patterns
    GROUP BY puzzle_id, button_effects, num_buttons, num_positions, parity_pattern
),

-- Recursive halving algorithm: iteratively reduce joltages to zero
recursive_halving_solver AS (
    -- Base case: start with target joltages
    SELECT
        puzzle_id,
        button_effects,
        num_buttons,
        num_positions,
        target_joltages AS current_goal,
        toUInt64(0) AS accumulated_cost,
        0 AS recursion_depth
    FROM puzzle_metadata
    
    UNION ALL
    
    -- Recursive case: apply pattern, subtract, halve, and continue
    SELECT
        puzzle_id,
        button_effects,
        num_buttons,
        num_positions,
        current_goal,
        min(accumulated_cost) AS accumulated_cost,
        min(recursion_depth) AS recursion_depth
    FROM (
        SELECT
            solver.puzzle_id,
            solver.button_effects,
            solver.num_buttons,
            solver.num_positions,
            
            -- New goal: (current - pattern) / 2
            arrayMap(
                i -> intDiv(
                    solver.current_goal[i] - pattern_tuple.1[i],
                    2
                ),
                range(1, solver.num_positions + 1)
            ) AS current_goal,
            
            -- Accumulate cost: pattern_cost * 2^depth
            solver.accumulated_cost + 
                toUInt64(pattern_tuple.2) * toUInt64(pow(2, solver.recursion_depth)) AS accumulated_cost,
            
            solver.recursion_depth + 1 AS recursion_depth
        FROM recursive_halving_solver solver
        INNER JOIN patterns_grouped_by_parity patterns
            ON patterns.puzzle_id = solver.puzzle_id
            AND patterns.parity_pattern = arrayMap(
                x -> if(x % 2 = 0, toUInt8(0), toUInt8(1)),
                solver.current_goal
            )
        ARRAY JOIN patterns.available_patterns AS pattern_tuple
        WHERE
            solver.recursion_depth < 100
            AND NOT arrayAll(x -> x = 0, solver.current_goal)
            -- Ensure pattern doesn't overshoot (feasibility constraint)
            AND arrayAll(
                i -> pattern_tuple.1[i] <= solver.current_goal[i],
                range(1, solver.num_positions + 1)
            )
    )
    GROUP BY puzzle_id, button_effects, num_buttons, num_positions, current_goal
),

part2_minimum_solutions AS (
    SELECT
        puzzle_id,
        min(accumulated_cost) AS minimum_cost
    FROM recursive_halving_solver
    WHERE arrayAll(x -> x = 0, current_goal)
    GROUP BY puzzle_id
),

-- Aggregate final solutions
combined_solutions AS (
    SELECT 'Part 1' AS part, sum(minimum_presses) AS solution -- 527 with my input
    FROM part1_minimum_solutions
    
    UNION ALL

    SELECT 'Part 2' AS part, sum(minimum_cost) AS solution -- 19810 with my input
    FROM part2_minimum_solutions
)

-- Combine results from both parts
SELECT * FROM combined_solutions settings use_query_cache=true, query_cache_share_between_users = 1, query_cache_nondeterministic_function_handling = 'save', query_cache_ttl = 80000000, result_overflow_mode = 'throw', read_overflow_mode = 'throw';
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/10)

---

## Day 11: The Reactor

**The Puzzle**: You are debugging a reactor control graph.

- **Part 1** asks to count all distinct paths from `you` to `out`.
- **Part 2** asks to count paths from `svr` to `out` that satisfy a constraint: they must visit both intermediate nodes `dac` and `fft`.

**How we solved this in ClickHouse SQL**: We solved this using a Recursive CTE to traverse the graph. To handle the constraint in Part 2, we carried "visited flags" in our recursion state. As we traversed the graph, we updated these boolean flags whenever we hit a checkpoint node. At the end, we simply filtered for paths where both flags were true.

**Implementation details**:

1. [`cityHash64`](https://clickhouse.com/docs/sql-reference/functions/hash-functions#cityHash64): String comparisons can be slow in large recursive joins. We converted the node names (like `svr`, `dac`) into deterministic 64-bit integers using `cityHash64`. This made the join operations significantly faster and reduced memory usage.

```sql
cityHash64('svr') AS svr_node
```

2. **State Tracking**: We added boolean columns to our recursive table to track state. This allowed us to solve the "must visit X and Y" constraint in a single pass without needing complex post-processing.

```sql
paths.visited_dac OR (edges.to_node = kn.dac_node) AS visited_dac
```

**Full Solution:**

```sql
WITH RECURSIVE
-- Define puzzle input 
input_wrapper AS (SELECT raw_blob AS input FROM aoc.input11),

-- Define key node identifiers
key_nodes AS (
    SELECT
        cityHash64('svr') AS svr_node,
        cityHash64('you') AS you_node,
        cityHash64('dac') AS dac_node,
        cityHash64('fft') AS fft_node,
        cityHash64('out') AS out_node
),

-- Parse input connections
raw_connections AS (
    SELECT splitByString(': ', raw) AS parsed_parts
    FROM format('TSV', 'raw String', (SELECT input FROM input_wrapper)::String)
),

parsed_connections AS (
    SELECT
        parsed_parts[1] AS input_node,
        splitByWhitespace(parsed_parts[2]) AS output_nodes
    FROM raw_connections
),

-- Create graph edges with hashed node IDs
graph_edges AS (
    SELECT
        cityHash64(input_node) AS from_node,
        cityHash64(arrayJoin(output_nodes)) AS to_node
    FROM parsed_connections
),

-- Part 2: Count paths from 'svr' to 'out' that visit both 'dac' and 'fft'
paths_from_svr AS (
    -- Base case: start at 'svr' node
    SELECT
        0 AS generation,
        svr_node AS current_node,
        0::UInt8 AS visited_dac,
        0::UInt8 AS visited_fft,
        1::UInt64 AS paths_count
    FROM key_nodes
    
    UNION ALL
    
    -- Recursive case: traverse edges and track checkpoint visits
    SELECT
        generation,
        current_node,
        visited_dac,
        visited_fft,
        sum(paths_count) AS paths_count
    FROM (
        SELECT
            paths.generation + 1 AS generation,
            edges.to_node AS current_node,
            paths.visited_dac OR (edges.to_node = kn.dac_node) AS visited_dac,
            paths.visited_fft OR (edges.to_node = kn.fft_node) AS visited_fft,
            paths.paths_count AS paths_count
        FROM paths_from_svr paths
        JOIN graph_edges edges ON edges.from_node = paths.current_node
        CROSS JOIN key_nodes kn
        WHERE
            edges.to_node != kn.out_node
            AND paths.generation < 628
    )
    GROUP BY generation, current_node, visited_dac, visited_fft
),

-- Part 1: Count all paths from 'you' to 'out'
paths_from_you AS (
    -- Base case: start at 'you' node
    SELECT
        0 AS generation,
        you_node AS current_node,
        1::UInt64 AS paths_count
    FROM key_nodes
    
    UNION ALL
    
    -- Recursive case: traverse edges
    SELECT
        generation,
        current_node,
        sum(paths_count) AS paths_count
    FROM (
        SELECT
            paths.generation + 1 AS generation,
            edges.to_node AS current_node,
            paths.paths_count AS paths_count
        FROM paths_from_you paths
        JOIN graph_edges edges ON edges.from_node = paths.current_node
        CROSS JOIN key_nodes kn
        WHERE
            edges.to_node != kn.out_node
            AND paths.generation < 628
    )
    GROUP BY generation, current_node
),

-- Part 1 solution: paths from 'you' to 'out'
part1_solution AS (
    SELECT sum(paths.paths_count) AS solution
    FROM paths_from_you paths
    JOIN graph_edges edges ON edges.from_node = paths.current_node
    CROSS JOIN key_nodes kn
    WHERE edges.to_node = kn.out_node
),

-- Part 2 solution: paths from 'svr' to 'out' visiting both checkpoints
part2_solution AS (
    SELECT sum(paths.paths_count) AS solution
    FROM paths_from_svr paths
    JOIN graph_edges edges ON edges.from_node = paths.current_node
    CROSS JOIN key_nodes kn
    WHERE
        edges.to_node = kn.out_node
        AND paths.visited_dac = 1
        AND paths.visited_fft = 1
),

solutions_combined as (
SELECT 
    'Part 1' AS part,
    (SELECT solution FROM part1_solution) AS solution -- 724 with my input

UNION ALL

SELECT 
    'Part 2' AS part,
    (SELECT solution FROM part2_solution) AS solution -- 473930047491888 with my input
)

SELECT * FROM solutions_combined;
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/11)

---

## Day 12: Christmas Tree Farm

**The Puzzle**: Elves need to pack irregular presents (defined by `#` grids) into rectangular regions. This looks like a complex 2D bin-packing problem. However, the puzzle input allows for a heuristic shortcut: checking if the _total area_ of the presents is less than or equal to the _total area_ of the region is sufficient.

**How we solved this in ClickHouse SQL**: Since we could solve this with a volume check, our solution focused on parsing. We converted the ASCII art shapes into binary grids (arrays of 1s and 0s) and calculated the area (count of 1s) for each. We then multiplied the requested quantity of each present by its area and compared the sum to the region's total size.

**Implementation details**:

1. [`replaceRegexpAll`](https://clickhouse.com/docs/sql-reference/functions/string-replace-functions#replaceRegexpAll): We used regex replacement to turn the visual `#` characters into `1` and `.` into `0`. This transformed the "art" into computable binary strings that we could parse into arrays.

2. [`arraySum`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arraySum): We used the lambda version of `arraySum` to perform a "dot product" operation. We multiplied the volume of each present by its area and summed the results in a single, clean expression.

```sql
arraySum(
    (volume, area) -> volume * area,
    requested_shape_volumes,
    areas_per_shape
)
```

**Full Solution:**

```sql
-- Define puzzle input 
WITH input_wrapper AS (SELECT trimRight(raw_blob,'\n') AS input FROM aoc.input12),

-- Split input into sections
input_sections AS (
    SELECT arrayMap(
        section -> splitByChar('\n', section),
        splitByString('\n\n', (SELECT input FROM input_wrapper)::String)
    ) AS sections
),

-- Extract regions section (last section)
regions_section AS (
    SELECT sections[-1] AS region_lines
    FROM input_sections
),

-- Extract shape sections (all except last)
shapes_sections AS (
    SELECT arrayJoin(
        arraySlice(sections, 1, length(sections) - 1)
    ) AS shape_lines
    FROM input_sections
),

-- Parse shape data
parsed_shapes AS (
    SELECT
        shape_lines,
        
        -- Transform shape lines: first line is name, rest is pattern
        arrayMap(
            line_index -> if(
                line_index = 1,
                -- First line: remove ':' from name
                replaceAll(shape_lines[line_index], ':', ''),
                -- Other lines: convert '#' to 1, '.' to 0
                replaceRegexpAll(
                    replaceRegexpAll(shape_lines[line_index], '#', '1'),
                    '\\.',
                    '0'
                )
            ),
            arrayEnumerate(shape_lines)
        ) AS transformed_lines
    FROM shapes_sections
),

-- Convert shape patterns to binary arrays
shape_patterns AS (
    SELECT
        transformed_lines,
        arrayMap(
            line -> arrayMap(
                char -> toUInt8(char),
                ngrams(line, 1)
            ),
            arraySlice(transformed_lines, 2)
        ) AS shape_grid
    FROM parsed_shapes
),

-- Calculate area needed for each shape
shape_areas AS (
    SELECT groupArray(
        arrayCount(
            cell -> cell = 1,
            arrayFlatten(shape_grid)
        )
    ) AS areas_per_shape
    FROM shape_patterns
),

-- Parse region specifications
parsed_regions AS (
    SELECT
        arrayJoin(
            arrayMap(
                line -> splitByString(': ', line),
                region_lines
            )
        ) AS region_parts
    FROM regions_section
),

-- Calculate region dimensions and requested volumes
region_specifications AS (
    SELECT
        region_parts,
        
        -- Calculate total region area (product of dimensions)
        arrayProduct(
            arrayMap(
                dim -> toUInt32(dim),
                splitByChar('x', region_parts[1])
            )
        ) AS total_region_area,
        
        -- Extract requested volumes for each shape
        arrayMap(
            vol -> toUInt8(vol),
            splitByChar(' ', region_parts[2])
        ) AS requested_shape_volumes
    FROM parsed_regions
),

-- Check if each region can fit the requested shapes
region_fit_analysis AS (
    SELECT
        total_region_area,
        requested_shape_volumes,
        areas_per_shape,
        
        -- Calculate total area needed: sum of (volume * area) for each shape
        arraySum(
            (volume, area) -> volume * area,
            requested_shape_volumes,
            areas_per_shape
        ) AS total_area_needed,
        
        -- Check if shapes fit in region
        total_area_needed <= total_region_area AS shapes_fit
    FROM region_specifications
    CROSS JOIN shape_areas
),

-- Count regions where shapes fit
solution AS (
    SELECT countIf(shapes_fit) AS solution
    FROM region_fit_analysis
)

-- Return final answer
SELECT solution -- 463 with my input
FROM solution
```

[Run code block](null)

[View full puzzle description](https://adventofcode.com/2025/day/12)

---

## Conclusion

The fact that we successfully solved all 12 of these puzzles using pure ClickHouse SQL demonstrates just how versatile our query engine truly is. This is all made possible because ClickHouse includes a massive standard library of built-in functions that bridge the gap between SQL and general-purpose programming. Throughout this challenge, we utilized over a dozen different [String Functions](https://clickhouse.com/docs/en/sql-reference/functions/string-functions) alongside the [format](https://clickhouse.com/docs/en/sql-reference/table-functions/format) table function to manipulate messy inputs into workable datasets. We relied heavily on [Array Functions](https://clickhouse.com/docs/en/sql-reference/functions/array-functions) like [`arrayMap`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayMap) and [`arrayProduct`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayProduct), but the real heroes were [`arrayReduce`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayReduce) and [`arrayFold`](https://clickhouse.com/docs/sql-reference/functions/array-functions#arrayFold), which allowed us to implement complex functional programming logic and maintain state across iterations. When combined with native [Recursive CTEs](https://clickhouse.com/docs/en/sql-reference/statements/select/with#recursive-cte) for pathfinding, [Distance Functions](https://clickhouse.com/docs/en/sql-reference/functions/distance-functions) for 3D geometry, [Polygon Functions](https://clickhouse.com/docs/sql-reference/functions/geo/polygons) for spatial analysis, and [Bitwise Operations](https://clickhouse.com/docs/en/sql-reference/functions/bit-functions) for logic gates, ClickHouse behaves less like a database and more like a high-performance vector computation engine. 

Due to our self-imposed constraints, these SQL solutions may not be as computationally optimal as implementations written in "real" programming languages like Rust or Python, but they nevertheless yield the exact same results. This experiment proves that when you have the right tools, problems that seem "impossible" in SQL become just another interesting data challenge for ClickHouse. You can view the full set of solution queries in our [ClickHouse/TreeHouse](https://github.com/ClickHouse/TreeHouse) repository.  


>Note: Thomas Neumann completed all Advent of Code puzzles in 2024 using Umbra DB.  His work can be found [here.](https://github.com/neumannt/aoc24)

