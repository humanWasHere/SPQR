proc Va_toucher { polarite direction my_handle top X0_dbu Y0_dbu precision securite layer_de_travail Passe_Grossiere} {

set PAS 0
set Nb_Polygon 0



	if {$polarite =="SPACE"} {


		while {$Nb_Polygon == 0} {
			set PAS [expr $PAS+$Passe_Grossiere]

			if {$direction =="X+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+$PAS*$precision/1000] [expr $Y0_dbu+1]
			} elseif {$direction =="X-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu-$PAS*$precision/1000] [expr $Y0_dbu+1]
			} elseif {$direction =="Y+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu+$PAS*$precision/1000]
			} elseif {$direction =="Y-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu-$PAS*$precision/1000]
			}


			eval $my_handle AND 9999 $layer_de_travail 9998
			set Nb_Polygon [eval $my_handle iterator count {poly} $top 9998]

					if {$PAS > $securite} {
					#puts "$direction trop loin"
					return
					}
			}

		$my_handle delete polygons $top 9999
		$my_handle delete polygons $top 9998

		set PAS [expr $PAS*$precision/1000]

		while {$Nb_Polygon !=0} {
			set PAS [expr $PAS -1 ]

			if {$direction =="X+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+$PAS] [expr $Y0_dbu+1]
			} elseif {$direction =="X-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu-$PAS] [expr $Y0_dbu+1]
			} elseif {$direction =="Y+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu+$PAS]
			} elseif {$direction =="Y-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu-$PAS]
			}


			eval $my_handle AND 9999 $layer_de_travail 9998
			set Nb_Polygon [eval $my_handle iterator count {poly} $top 9998]

					if {[expr $PAS*1000/$precision] > $securite} {
					#puts "$direction trop loin"
					return
					}
				$my_handle delete polygons $top 9999
				$my_handle delete polygons $top 9998
				#puts $PAS

			}
		if {$direction =="X+"} {
		return [expr $X0_dbu+$PAS]
		} elseif {$direction =="X-"} {
		return [expr $X0_dbu-$PAS]
		} elseif {$direction =="Y+"} {
		return [expr $Y0_dbu+$PAS]
		} elseif {$direction =="Y-"} {
		return [expr $Y0_dbu-$PAS]
		}
	}



	if {$polarite =="CD"} {

		while {$Nb_Polygon == 0} {
			set PAS [expr $PAS+$Passe_Grossiere]

			if {$direction =="X+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+$PAS*$precision/1000] [expr $Y0_dbu+1]
			} elseif {$direction =="X-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu-$PAS*$precision/1000] [expr $Y0_dbu+1]
			} elseif {$direction =="Y+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu+$PAS*$precision/1000]
			} elseif {$direction =="Y-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu-$PAS*$precision/1000]
			}


			eval $my_handle NOT 9999 $layer_de_travail 9998
			set Nb_Polygon [eval $my_handle iterator count {poly} $top 9998]

					if {$PAS > $securite} {
					#puts "$direction trop loin"
					return
					}
			}

		$my_handle delete polygons $top 9999
		$my_handle delete polygons $top 9998

		set PAS [expr $PAS*$precision/1000]

		while {$Nb_Polygon !=0} {
			set PAS [expr $PAS -1 ]

			if {$direction =="X+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+$PAS] [expr $Y0_dbu+1]
			} elseif {$direction =="X-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu-$PAS] [expr $Y0_dbu+1]
			} elseif {$direction =="Y+"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu+$PAS]
			} elseif {$direction =="Y-"} {
			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu-$PAS]
			}


			eval $my_handle NOT 9999 $layer_de_travail 9998
			set Nb_Polygon [eval $my_handle iterator count {poly} $top 9998]

					if {[expr $PAS*1000/$precision] > $securite} {
					#puts "$direction trop loin"
					return
					}
				$my_handle delete polygons $top 9999
				$my_handle delete polygons $top 9998

			}
		if {$direction =="X+"} {
		return [expr $X0_dbu+$PAS]
		} elseif {$direction =="X-"} {
		return [expr $X0_dbu-$PAS]
		} elseif {$direction =="Y+"} {
		return [expr $Y0_dbu+$PAS]
		} elseif {$direction =="Y-"} {
		return [expr $Y0_dbu-$PAS]
		}

	}


}
proc dim_micron {dbu_plus dbu_moins precision} {

	if {$dbu_plus !="" && $dbu_moins !=""} {
		set dim [expr ($dbu_plus - $dbu_moins)/$precision]
	} else {
		set dim 0
	}
return $dim
}


set Mon_layout Mon_gds
layout create $Mon_layout FEED_ME_GDS -dt_expand -preservePaths

set top [$Mon_layout topcell]

set layer_de_travail_base {FEED_ME_LAYER}
#puts $layer_de_travail_base
set Zone_decoupe FEED_ME_SEARCH_AREA
set precision FEED_ME_PRECISION
set demi_boite [expr (($Zone_decoupe*$precision)/2)]
set correction FEED_ME_CORRECTION
set Passe_Grossiere 15
set Passe_Grossiere_pitch 1
set Ma_sortie FEED_ME_OUTPUT

# set Mon_fichier [open "$Ma_sortie" w+]
# puts $Mon_fichier [concat Gauge , Layer , Polarite , X_dimension(nm) , Y_dimension(nm) , min_dimension(nm), complementaire(nm), pitch_of_min_dim(nm)]
# close $Mon_fichier


 set coordonnees { FEED_ME_COORDINATES
 }

puts "Beginning of measurement"

#set layer_error "Layer not found"
set pitch_error "Pitch non symetrical"
set iso "ISO"
set limite_iso_micron 1.5
set TIME_start [clock clicks -milliseconds]
set Compteur 0

set Mon_fichier [open "$Ma_sortie" w+]
puts $Mon_fichier "Gauge , Layer , Polarity (polygon) , X_dimension(nm) , Y_dimension(nm) ,pitch_x(nm),pitch_y(nm), min_dimension(nm), complementary(nm), pitch_of_min_dim(nm)"


foreach layer_de_travail $layer_de_travail_base {


	foreach gauge $coordonnees {


		###########################################################################
		#Compteur pour le pourcentage
		###########################################################################
		set Compteur [expr $Compteur + 1]
		set avancement [expr round (($Compteur+0.0)/[llength $coordonnees]/[llength $layer_de_travail_base]*100)]
		set nb_total [expr [llength $coordonnees]*[llength $layer_de_travail_base]]

		set X0_dbu [expr ([lindex $gauge 1]*$precision/$correction)]
		set Y0_dbu [expr ([lindex $gauge 2]*$precision/$correction)]

		set Xmin [expr $X0_dbu-$demi_boite]
		set Xmax [expr $X0_dbu+$demi_boite]
		set Ymin [expr $Y0_dbu-$demi_boite]
		set Ymax [expr $Y0_dbu+$demi_boite]

		set my_handle pour_mesure
		eval layout copy $Mon_layout $my_handle $top 0 1000 [concat $Xmin $Ymin $Xmax $Ymax] 1

		#check if layer exist in the cut
		set check [$my_handle exists layer $layer_de_travail]

		if {$check == 1} {

			$my_handle create layer 9999
			$my_handle create layer 9998

			###########################################################################
			######                                                               ######
			######               Auto detection CD ou Space                      ######
			######                                                               ######
			###########################################################################

			$my_handle create polygon $top 9999 [expr $X0_dbu] [expr $Y0_dbu] [expr $X0_dbu+1] [expr $Y0_dbu+1]
			eval $my_handle AND 9999 $layer_de_travail 9998
			set Nb_Polygon [eval $my_handle iterator count {poly} $top 9998]

			if {$Nb_Polygon>0} {
				set polarite "CD"
			} else {
				set polarite "SPACE"
			}

			$my_handle delete polygons $top 9999
			$my_handle delete polygons $top 9998

			###########################################################################
			######                                                               ######
			######         mesure en X et Y                                      ######
			######                                                               ######
			###########################################################################

			###########################################################################
			# Recherche dimension x et y
			###########################################################################
			set X_plus  [ Va_toucher $polarite X+ $my_handle $top $X0_dbu $Y0_dbu $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]
			set X_moins [ Va_toucher $polarite X- $my_handle $top $X0_dbu $Y0_dbu $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]
			set Y_plus  [ Va_toucher $polarite Y+ $my_handle $top $X0_dbu $Y0_dbu $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]
			set Y_moins [ Va_toucher $polarite Y- $my_handle $top $X0_dbu $Y0_dbu $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]

			if {$X_plus !="" && $X_moins !=""} {
				set taille_en_X [expr ($X_plus - $X_moins)/$precision]
			} else {
				set taille_en_X 0
			}

			if {$Y_plus !="" && $Y_moins !=""} {
				set taille_en_Y [expr ($Y_plus - $Y_moins)/$precision]
			} else {
				set taille_en_Y 0
			}


			if {$taille_en_X !=0 && $taille_en_Y !=0} {
				set le_plus_petit [expr min($taille_en_X,$taille_en_Y)]
			} else {
				set le_plus_petit [expr max($taille_en_X,$taille_en_Y)]
			}
			# if {$taille_en_X == 0 && $taille_en_Y == 0}
				# should not define value to 0 / return an error / don't allow measurement

			###########################################################################
			# Recherche pitch
			###########################################################################
			#recentrage x0 y0
			set X0_dbu_new [expr $X_moins + ($taille_en_X/2 * $precision)]
			set Y0_dbu_new [expr $Y_moins + ($taille_en_Y/2 * $precision)]


			#recherche pitch
			set x_for_pitch_right [expr $X0_dbu_new + ($taille_en_X/2 * $precision) + 1]
			set x_for_pitch_left  [expr $X0_dbu_new - ($taille_en_X/2 * $precision) - 1]
			set y_for_pitch_up    [expr $Y0_dbu_new + ($taille_en_Y/2 * $precision) + 1]
			set y_for_pitch_down  [expr $Y0_dbu_new - ($taille_en_Y/2 * $precision) - 1]

			#Inversion de la polarite pour la recherche de pitch
			if {$polarite == "CD"}    {set polarite_for_pitch "SPACE"}
			if {$polarite == "SPACE"} {set polarite_for_pitch "CD"}
			
			#Determination du plus petit pour recherche le pitch seulement sur cette dimension et fonctionne seulement si le pitch est le même des deux côtés
			proc measure_pitch {measurement_direction pitch_left_coord pitch_right_coord pitch_down_coord pitch_up_coord} {
				global polarite_for_pitch my_handle top precision Zone_decoupe layer_de_travail Passe_Grossiere iso le_plus_petit pitch_error
				# Measure pitch in the specified direction
				# left/down
				set pitch_left_down_moins [Va_toucher $polarite_for_pitch $measurement_direction- $my_handle $top $pitch_left_coord $pitch_down_coord $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]
				set pitch_left_down_plus  [Va_toucher $polarite_for_pitch $measurement_direction+ $my_handle $top $pitch_left_coord $pitch_down_coord $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]
				set dimension_complementaire_left_down [dim_micron $pitch_left_down_plus $pitch_left_down_moins $precision]

				# right/up
				set pitch_right_up_moins [Va_toucher $polarite_for_pitch $measurement_direction- $my_handle $top $pitch_right_coord $pitch_up_coord $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]
				set pitch_right_up_plus  [Va_toucher $polarite_for_pitch $measurement_direction+ $my_handle $top $pitch_right_coord $pitch_up_coord $precision [expr $Zone_decoupe*1000] $layer_de_travail $Passe_Grossiere]
				set dimension_complementaire_right_up [dim_micron $pitch_right_up_plus $pitch_right_up_moins $precision]

				# Determine pitch in the specified direction
				if {$dimension_complementaire_left_down == $dimension_complementaire_right_up} {
					if {$dimension_complementaire_left_down == $iso} {
						set pitch $iso
					} else {
						set pitch [expr $le_plus_petit + $dimension_complementaire_left_down]
					}
				} else {
					set pitch $pitch_error
					set dimension_complementaire_left_down $pitch_error
				}

				# Return pitch in the specified direction
				return $pitch
			}

			# Call measure_pitch procedure for both X and Y directions
			set pitch_x [measure_pitch X $x_for_pitch_left $x_for_pitch_right $Y0_dbu $Y0_dbu]
			set pitch_y [measure_pitch Y $X0_dbu $X0_dbu $y_for_pitch_down $y_for_pitch_up]

			# Output pitch in both X and Y directions
			# puts "Pitch in X direction: $pitch_x"
			# puts "Pitch in Y direction: $pitch_y"
			if {$le_plus_petit == $taille_en_X} {set pitch $pitch_x} else {set pitch $pitch_y}

			#puts [concat ($Compteur/$nb_total:$avancement%): [lindex $gauge 0] | Polarite: $polarite | $layer_de_travail | X_dimension: $taille_en_Xµm | Y_dimension: $taille_en_Yµm | min_dimension: $le_plus_petitµm | Complementary: $dimension_complementaire_plusµm | Pitch: $pitchµm]
			puts [concat ($Compteur/$nb_total:$avancement%): [lindex $gauge 0] | Polarite: $polarite | min_dimension: $le_plus_petit | Pitch: $pitch | pitch_x_y $pitch_x $pitch_y ]

			###########################################################################
			# Ecriture dans le fichier
			###########################################################################
			set taille_en_X_nm [expr $taille_en_X*1000]
			set taille_en_Y_nm [expr $taille_en_Y*1000]
			set le_plus_petit_nm [expr $le_plus_petit*1000]

			if {$pitch_x != $pitch_error && $pitch_x != $iso} {
				set pitchx_nm [expr $pitch_x *1000]
			} else {
				set pitchx_nm $pitch_x
			}
			if {$pitch_y != $pitch_error && $pitch_y != $iso} {
				set pitchy_nm [expr $pitch_y *1000]
			} else {
				set pitchy_nm $pitch_y
			}
			if {$pitch != $pitch_error && $pitch != $iso} {
				set pitch_nm [expr $pitch *1000]
				#set pitchx_nm [expr $pitch_x *1000]
				#set pitchy_nm [expr $pitch_y *1000]
				set dimension_complementaire_nm [expr $pitch_nm-$le_plus_petit_nm]
			} elseif { $pitch == $pitch_error } {
				set dimension_complementaire_nm $pitch_error
				set pitch_nm $pitch_error
			} elseif { $pitch == $iso } {
			    set pitch_nm $iso
				set dimension_complementaire_nm $iso
			}

			puts $Mon_fichier [concat [lindex $gauge 0],$layer_de_travail,$polarite,$taille_en_X_nm,$taille_en_Y_nm,$pitchx_nm,$pitchy_nm,$le_plus_petit_nm,$dimension_complementaire_nm,$pitch_nm]
			update
			layout delete $my_handle
		} else {
			puts [concat ($Compteur/$nb_total:$avancement%): [lindex $gauge 0] " does not exist on layer $layer_de_travail"]
			puts $Mon_fichier [concat [lindex $gauge 0],$layer_de_travail,unknown,unknown,unknown,unknown,unknown,unknown]
			layout delete $my_handle
			#puts "Gauge [lindex $gauge 0] doesn't exist on layer $layer_de_travail"
		}
	}
}
close $Mon_fichier

layout delete $Mon_layout
set TIME_taken [expr ([clock clicks -milliseconds] - $TIME_start)/1000]

puts "Gauge measurement finished in $TIME_taken second(s)"
