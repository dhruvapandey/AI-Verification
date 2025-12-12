module router (
    input logic clk,
    input logic rst_n,
    
    // Inputs
    input logic [3:0]  req_i,      // Traffic (4 bits)
    input logic [31:0] data_n_i,
    input logic [31:0] data_s_i,
    input logic [31:0] data_e_i,
    input logic [31:0] data_w_i,
    
    // CONTROL INPUT: Backpressure
    // 1 = Receiver Ready (Drain)
    // 0 = Receiver Stuck (Congestion)
    input logic        yumi_i,     

    // Outputs
    output logic [31:0] data_o,
    output logic        valid_o,
    output logic        busy_o
);

    // 1. DEFINITIONS FOR DEPTH 64
    logic [31:0] buffer [0:63];     // Size 64
    logic [5:0]  write_ptr, read_ptr; 
    logic [6:0]  count;             // 7 bits to store "64"

    // Helper Signals
    logic write_en;
    logic read_en;

    // 2. LOGIC GATES
    // Can we write? Yes, if there is a request AND space in buffer.
    assign write_en = (|req_i) && (count < 64);
    
    // Can we read? Yes, if buffer has data AND receiver is ready (yumi).
    assign read_en  = (count > 0) && yumi_i;


    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            write_ptr <= 0;
            read_ptr  <= 0;
            count     <= 0;
            busy_o    <= 0;
            valid_o   <= 0;
            data_o    <= 0;
        end else begin
            
            // --- WRITE OPERATION ---
            if (write_en) begin
                if (req_i[0])      buffer[write_ptr] <= data_n_i;
                else if (req_i[1]) buffer[write_ptr] <= data_s_i;
                else if (req_i[2]) buffer[write_ptr] <= data_e_i;
                else if (req_i[3]) buffer[write_ptr] <= data_w_i;
                
                write_ptr <= write_ptr + 1;
            end

            // --- READ OPERATION ---
            if (read_en) begin
                data_o    <= buffer[read_ptr];
                valid_o   <= 1;
                read_ptr  <= read_ptr + 1;
            end else begin
                valid_o <= 0;
            end

            // --- COUNT UPDATE (The Critical Fix) ---
            if (write_en && !read_en) begin
                count <= count + 1;          // Fill
            end 
            else if (!write_en && read_en) begin
                count <= count - 1;          // Drain
            end
            // If (write_en && read_en), count stays same (Net change 0)
            // If (!write_en && !read_en), count stays same

            // --- BUSY SIGNAL ---
            // Assert busy if we are nearly full (e.g., >= 60)
            if (count >= 60) busy_o <= 1; 
            else             busy_o <= 0;
        end
    end

    initial begin
        $dumpfile("router.vcd");
        $dumpvars(0, router);
    end

endmodule
