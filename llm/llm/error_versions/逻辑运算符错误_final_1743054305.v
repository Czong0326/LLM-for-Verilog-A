 // Copyright (c) 2024 Zhejiang Hikstor Technology Ltd.
 // All rights reserved.
 //
 // Engineer: xiexuejie@hikstor.com
 // 

`include"constants.h"
`include"discipline.h"

module sotmodel(p,q,n);
		inout p,q,n;
	
		electrical p,q,n;

		parameter real Rsot0 = 800;
		parameter real Rp0 = 11k;
		parameter integer IniState = 1 from [0:1];
		parameter real Hx = 20;
		parameter real Iop = 800u;
		parameter real Rsot_mis = 1;
		parameter real Rp_mis = 1;
		parameter real TMR_mis = 1;
		 
		real Rmtj, Rsot, Isot;
		integer mtj_state;
		integer sign_Hx, sign_Iap2p, sign_Ip2ap;
		integer switch_ap2p, switch_p2ap;
		real Iap2p, Ip2ap;
		real Iap2pt, Ip2apt;
		real Istt, Vmtj;
		real time_ap2p, time_p2ap;
		real a, b, c;
		real Rp, Rap;
		real TMR0, TMR;
		real timer1, timer2;
		real width;

		analog begin
	
				@(initial_step) begin
						mtj_state = IniState;
						width = 5;
						TMR0 = 1.2;
						
						case(Hx)
								20,-20: begin
										Iap2pt = Iop;
										Ip2apt = Iop;
								end
						default:
								$strobe("Warning: Specified Hx = %f is not defined\n",Hx);
						endcase
			
						sign_Hx = (Hx>0)?1:-1;
						sign_Iap2p = -sign_Hx;
						sign_Ip2ap = -sign_Iap2p;
			
						a= 0.1729;
						b= -0.1315;
						c= 0.4475;
			
						Iap2p = sign_Iap2p*Iap2pt;
						Ip2ap = sign_Ip2ap*Ip2apt;
	
						Rsot = Rsot0*Rsot_mis;
						Rp = Rp0*Rp_mis;
						Rap = Rp*(TMR0*TMR_mis+1);
						Rmtj = mtj_state*Rap+(1-mtj_state)*Rp;
			
				end
		
				Isot = V(q,n)/Rsot;
				Istt = (2*V(p,q)+2*V(p,n))/(4*Rmtj+Rsot);
				Vmtj = Istt*Rmtj;
		
				TMR0 = 1/(a*Vmtj*Vmtj-b*abs(Vmtj)+c)-1;
				TMR = TMR0*TMR_mis;
				Rap = (1+TMR)*Rp;
		
				switch_ap2p = sign_Iap2p>0?Isot>=Iap2p:Isot<=Iap2p;
				switch_p2ap = sign_Ip2ap>0?Isot>=Ip2ap:Isot<=Ip2ap;
			
				if (analysis("tran")) begin
						@(cross(switch_ap2p-0.5,+1)) begin
								timer1 = $abstime*1E9;
						end
						time_ap2p = $abstime*1E9 - timer1;
		
						@(cross(switch_p2ap-0.5,+1)) begin
								timer2 = $abstime*1E9;
						end
						time_p2ap = $abstime*1E9 - timer2;
			
						if (mtj_state==1) begin
								Rmtj = Rap;
								if (switch_ap2p==1 || time_ap2p>=width) begin
										mtj_state = 0;
										Rmtj = Rp;
										if (abs(Isot)<=Iap2pt+10u) begin
												Rmtj = Rap-(Rap-Rp)/10u*(abs(Isot)-Iap2pt);
										end
								end
						end else if (mtj_state==0) begin
								Rmtj = Rp;
								if (switch_p2ap==1 && time_p2ap>=width) begin
										mtj_state = 1;
										Rmtj = Rap;
										if (abs(Isot)<=Ip2apt+10u) begin
												Rmtj = Rp+(Rap-Rp)/10u*(abs(Isot)-Ip2apt);
										end
								end
						end
				end else if (analysis("dc")) begin
						if (mtj_state==1) begin
								Rmtj = Rap;
								if (switch_ap2p==1) begin
										mtj_state = 0;
										Rmtj = Rp;
										if (abs(Isot)<=Iap2pt+10u) begin
												Rmtj = Rap-(Rap-Rp)/10u*(abs(Isot)-Iap2pt);
										end
								end
						end else if (mtj_state==0) begin
								Rmtj = Rp;
								if (switch_p2ap==1) begin
										mtj_state = 1;
										Rmtj = Rap;
										if (abs(Isot)<=Ip2apt+10u) begin
												Rmtj = Rp+(Rap-Rp)/10u*(abs(Isot)-Ip2apt);
										end
								end
						end
				end
				
				if (abs(Vmtj) > 0.3) begin
						$strobe("Warning: The voltage applied to MTJ exceeds 0.3V, which is undefined.\n");
				end
		
				I(p) <+ Istt;
				I(q) <+ V(q,n)/Rsot-0.5*Istt;
				I(n) <+ -V(q,n)/Rsot-0.5*Istt;
		end
endmodule
		

