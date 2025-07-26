


module test400(
    input sys_clk,  // 系统时钟
    input sys_rst,  // 系统复位
    output busy,    // 状态机正在计算
    output reg succ,
    output reg fail,
    output reg lazy_succ,
    input int file_fd,
    input ctrl_jump_flag_o,
    input rst,

    input gclk,     // 用户时钟
    input grst      // 用户复位
);
parameter TIMER_WIDTH = 48;
reg [TIMER_WIDTH - 1 : 0] timer = 0;
always @(posedge gclk or posedge grst) begin
    if(grst) begin
        timer <= '0;
    end
    else begin
        timer <= timer + 1'b1;
    end
end


parameter SVA_FSM_NUM = 128 ;//22;
parameter SVA_FSM_WIDTH = $clog2(SVA_FSM_NUM);
typedef enum  int {S0 = 0  , 
    SEND = -1   , 
    SLAZY = -2   , S1 = 1  , S2 = 2  , S3 = 3  , S4 = 4  , S5 = 5  , S6 = 6  , S7 = 7  , S8 = 8  , S9 = 9  , S10 = 10  , S11 = 11  , S12 = 12  , S13 = 13  , S14 = 14  , S15 = 15  , S16 = 16  , S17 = 17  , S18 = 18  , S19 = 19 
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


reg ctrl_jump_flag_o_delay;
always @(posedge gclk)begin 
    ctrl_jump_flag_o_delay <= ctrl_jump_flag_o;
end


reg rst_delay;
always @(posedge gclk)begin 
    rst_delay <= rst;
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((!ctrl_jump_flag_o_delay)  && (rst_delay) )
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
                
            else if (((ctrl_jump_flag_o_delay)  && (rst_delay) )
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
    if (ctrl_jump_flag_o_delay) $fwrite(file_fd,"ctrl_jump_flag_o\t");
    else $fwrite(file_fd,"!ctrl_jump_flag_o\t");
    if (rst_delay) $fwrite(file_fd,"rst\t");
    else $fwrite(file_fd,"!rst\t");
    $fwrite(file_fd,"# 跳转状态 : %0d\tactive=%d\t@%0d\n", get_next_sva_info.fsm_cur ,get_next_sva_info.active,$time);
    return get_next_sva_info;
endfunction

endmodule