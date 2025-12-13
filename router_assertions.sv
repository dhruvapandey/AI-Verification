module router_assertions (
    input logic clk,
    input logic rst_n,
    input logic [6:0] count
    // Add other signals you need to monitor
);

// Insert this BEFORE 'endmodule' in router.sv

// --- VERIFICATION ONLY (Hidden from synthesis) ---
`ifdef ASSERT_ON

    // 1. Create a "shadow" register to remember the past
    // Icarus sometimes struggles with $past(), so we do it manually.
    logic [6:0] count_prev;

    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            count_prev <= 0;
        end else begin
            // Update the history for the NEXT cycle
            count_prev <= count; 
        end
    end

    // 2. The Police Check (Run on every clock edge)
    always_ff @(posedge clk) begin
        if (rst_n) begin
            
            // CHECK 1: Smoothness (No Jumping)
            // If we grew, we must not have grown by more than 1
            if (count > count_prev) begin
                assert (count - count_prev <= 1) 
                else $fatal(1, "🚨 BUG: Counter jumped up illegally! (Prev: %0d, Curr: %0d)", count_prev, count);
            end

            // If we shrank, we must not have shrunk by more than 1
            if (count_prev > count) begin
                assert (count_prev - count <= 1) 
                else $fatal(1, "🚨 BUG: Counter jumped down illegally! (Prev: %0d, Curr: %0d)", count_prev, count);
            end

            // CHECK 2: Bounds (No Overflow/Underflow)
            assert (count <= 64) 
            else $fatal(1, "🚨 BUG: Buffer Overflow! Count is %0d", count);
            
        end
    end

`endif

endmodule
