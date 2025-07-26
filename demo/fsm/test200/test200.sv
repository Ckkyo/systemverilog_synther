


module test200(
    input sys_clk,  // 系统时钟
    input sys_rst,  // 系统复位
    output busy,    // 状态机正在计算
    output reg succ,
    output reg fail,
    output reg lazy_succ,
    input int file_fd,
    input arready_s0,
    input arvalid_s0,

    input gclk,     // 用户时钟
    input grst      // 用户复位
);
parameter TIMER_WIDTH = 1;
reg [TIMER_WIDTH - 1 : 0] timer = 0;
always @(posedge gclk or posedge grst) begin
    if(grst) begin
        timer <= '0;
    end
    else begin
        timer <= timer + 1'b1;
    end
end


parameter SVA_FSM_NUM = 1 ;//67;
parameter SVA_FSM_WIDTH = $clog2(SVA_FSM_NUM);
typedef enum  int {S0 = 0  , 
    SEND = -1   , 
    SLAZY = -2   , S1 = 1  , S2 = 2  , S3 = 3  , S4 = 4  , S5 = 5  , S6 = 6  , S7 = 7  , S8 = 8  , S9 = 9  , S10 = 10  , S11 = 11  , S12 = 12  , S13 = 13  , S14 = 14  , S15 = 15  , S16 = 16  , S17 = 17  , S18 = 18  , S19 = 19  , S20 = 20  , S21 = 21  , S22 = 22  , S23 = 23  , S24 = 24  , S25 = 25  , S26 = 26  , S27 = 27  , S28 = 28  , S29 = 29  , S30 = 30  , S31 = 31  , S32 = 32  , S33 = 33  , S34 = 34  , S35 = 35  , S36 = 36  , S37 = 37  , S38 = 38  , S39 = 39  , S40 = 40  , S41 = 41  , S42 = 42  , S43 = 43  , S44 = 44  , S45 = 45  , S46 = 46  , S47 = 47  , S48 = 48  , S49 = 49  , S50 = 50  , S51 = 51  , S52 = 52  , S53 = 53  , S54 = 54  , S55 = 55  , S56 = 56  , S57 = 57  , S58 = 58  , S59 = 59  , S60 = 60  , S61 = 61  , S62 = 62  , S63 = 63  , S64 = 64 
} sva_fsm_t;
typedef struct packed {
    bit active;
    bit [TIMER_WIDTH - 1 : 0] start_period; // 从 grst 结束复位开始计算
    sva_fsm_t fsm_cur;
} sva_info_t;

sva_info_t sva_infos[SVA_FSM_NUM]; //用 sva_info_rd_idx_valid_vec 记录数据是否有效
sva_info_t sva_info_st0 = '{ active : 1'b1, start_period : timer, fsm_cur : S0 };

reg gclk_d0, gclk_d1;
wire gclk_posedge_flag;
wire gclk_negedge_flag;
always @(posedge sys_clk or posedge sys_rst) begin
    if(sys_rst) begin
        gclk_d0 <= '0;
        gclk_d1 <= '0;
    end
    else if (grst) begin
        gclk_d0 <= '0;
        gclk_d1 <= '0;
    end
    else begin 
        gclk_d0 <= gclk;
        gclk_d1 <= gclk_d0;
    end
end
assign gclk_posedge_flag = ( gclk_d0) & (~gclk_d1);
assign gclk_negedge_flag = (~gclk_d0) & ( gclk_d1);


reg arready_s0_delay;
always @(posedge gclk)begin 
    arready_s0_delay <= arready_s0;
end


reg arvalid_s0_delay;
always @(posedge gclk)begin 
    arvalid_s0_delay <= arvalid_s0;
end




// EVAL 计算 sva_infos 中的 fsm_cur, EVAL1 则会从构建的 sva_info_st0 开始计算一个状态, 并且填到 sva_infos 的最后
typedef enum reg[3:0] { IDLE, EVAL0 } ctrl_fsm_t;
ctrl_fsm_t ctrl_fsm;

reg [SVA_FSM_WIDTH  : 0] sva_info_rd_idx             = 0;
reg [SVA_FSM_NUM    : 0] sva_info_rd_idx_valid_vec   = 0;
reg                      sva_info_rd_idx_valid       = 0;
reg [SVA_FSM_WIDTH  : 0] sva_info_wr_idx             = 0;
sva_info_t sva_info_cur ; // 当前的 sva_info
sva_info_t sva_info_next; // 当前的 sva_info

always @(posedge sys_clk or posedge sys_rst) begin
    if(sys_rst) begin
        ctrl_fsm <= IDLE;
        sva_info_rd_idx <= '0;
        sva_info_rd_idx_valid_vec <= '0;
        sva_info_rd_idx_valid <= '0;
        sva_info_wr_idx <= '0;
        sva_info_cur    <= '0;
    end
    else begin
        case(ctrl_fsm)
            IDLE: begin
                if(gclk_posedge_flag) begin
                    ctrl_fsm        <= EVAL0;
                    sva_info_cur    <= sva_infos[0];
                    sva_info_rd_idx_valid <= sva_info_rd_idx_valid_vec[0];
                    sva_info_rd_idx_valid_vec[0] <= 1'b0;
                    // sva_info_rd_idx <= sva_info_rd_idx + 1'b1;
                end
            end
            EVAL0: begin
                if(sva_info_cur.active && sva_info_rd_idx_valid) begin
                    ctrl_fsm        <= EVAL0;
                    sva_info_cur    <= sva_infos[sva_info_rd_idx + 1'b1];
                    sva_info_rd_idx_valid <= sva_info_rd_idx_valid_vec[sva_info_rd_idx + 1'b1];
                    sva_info_rd_idx_valid_vec[sva_info_rd_idx + 1'b1] <= 1'b0;
                    sva_info_rd_idx <= sva_info_rd_idx + 1'b1;

                    sva_info_next = get_next_sva_info(sva_info_cur);
                    sva_infos[sva_info_wr_idx] <= sva_info_next;
                    sva_info_wr_idx            <= sva_info_wr_idx + (sva_info_next.active == 1'b1 ? 1'b1 : 1'b0);

                    sva_info_rd_idx_valid_vec[sva_info_wr_idx] <= (sva_info_next.active == 1'b1 ? 1'b1 : 1'b0);
                end
                else begin 
                    ctrl_fsm        <= IDLE;

                    sva_info_next = get_next_sva_info(sva_info_st0);
                    sva_infos[sva_info_wr_idx] <= sva_info_next;
                    sva_info_wr_idx            <= sva_info_wr_idx + (sva_info_next.active == 1'b1 ? 1'b1 : 1'b0);

                    sva_info_rd_idx_valid_vec[sva_info_wr_idx] <= (sva_info_next.active == 1'b1 ? 1'b1 : 1'b0);

                    sva_info_rd_idx <= '0;
                    sva_info_wr_idx <= '0;

                end
            end
            default: begin
                ctrl_fsm <= IDLE;
                sva_info_rd_idx <= '0;
                sva_info_rd_idx_valid_vec <= '0;
                sva_info_rd_idx_valid <= '0;
                sva_info_wr_idx <= '0;
                sva_info_cur    <= '0;
            end
        endcase
    end
end

function sva_info_t get_next_sva_info(sva_info_t sva_info_cur);
    get_next_sva_info = '0;
    succ = 1'b0;
    lazy_succ = 1'b0;
    fail = 1'b0;
    case(sva_info_cur.fsm_cur)
        
            
        S0: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay)  && (arvalid_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arvalid_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SLAZY;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay)  && (arvalid_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S1;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        SEND: begin
            get_next_sva_info.active = 1'b0;
        end
        
            
        SLAZY: begin
            get_next_sva_info.active = 1'b0;
        end
            
        
            
        S1: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S2;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S2: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S3;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S3: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S4;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S4: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S5;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S5: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S6;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S6: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S7;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S7: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S8;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S8: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S9;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S9: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S10;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S10: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S11;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S11: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S12;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S12: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S13;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S13: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S14;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S14: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S15;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S15: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S16;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S16: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S17;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S17: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S18;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S18: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S19;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S19: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S20;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S20: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S21;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S21: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S22;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S22: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S23;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S23: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S24;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S24: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S25;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S25: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S26;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S26: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S27;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S27: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S28;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S28: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S29;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S29: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S30;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S30: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S31;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S31: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S32;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S32: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S33;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S33: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S34;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S34: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S35;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S35: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S36;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S36: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S37;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S37: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S38;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S38: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S39;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S39: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S40;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S40: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S41;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S41: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S42;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S42: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S43;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S43: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S44;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S44: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S45;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S45: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S46;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S46: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S47;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S47: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S48;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S48: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S49;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S49: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S50;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S50: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S51;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S51: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S52;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S52: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S53;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S53: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S54;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S54: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S55;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S55: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S56;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S56: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S57;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S57: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S58;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S58: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S59;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S59: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S60;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S60: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S61;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S61: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S62;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S62: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S63;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S63: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else if (((!arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = S64;
                    
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
            
        S64: begin
            
            if(0)begin 

            end
                
            else if (((arready_s0_delay) )
                    ) begin
                get_next_sva_info.active = 1'b1;
                get_next_sva_info.fsm_cur = SEND;
                if (get_next_sva_info.fsm_cur == SEND) begin
                    $fwrite(file_fd,"finish\n");
                    succ = 1'b1;
                end
                else if (get_next_sva_info.fsm_cur == SLAZY) begin
                    lazy_succ = 1'b1;
                end
            end
                
            else begin 
                get_next_sva_info.active = 1'b0;
                $fwrite(file_fd,"error\n");
                fail = 1'b1;
            end
        end
        
        default: begin
            get_next_sva_info = '0;
        end
    endcase
    $fwrite(file_fd,"# 当前状态 : %0d\t", sva_info_cur.fsm_cur );
    $fwrite(file_fd,"输入 : ");
    if (arready_s0_delay) $fwrite(file_fd,"arready_s0\t");
    else $fwrite(file_fd,"!arready_s0\t");
    if (arvalid_s0_delay) $fwrite(file_fd,"arvalid_s0\t");
    else $fwrite(file_fd,"!arvalid_s0\t");
    $fwrite(file_fd,"# 跳转状态 : %0d\tactive=%d\t@%0d\n", get_next_sva_info.fsm_cur ,get_next_sva_info.active,$time);
    return get_next_sva_info;
endfunction

endmodule