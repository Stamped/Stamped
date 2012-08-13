
TODO:
    * integrate current list of modified variables into page URL via History.js 
    * create gallery page containing an overview of all sketches
    * be able to toggle between code view and description / walkthrough.
    * pass through sketches for a round of cleanup
        * consistency across sketches
        * verbose comments
        * consider abstracted variables very carefully
            * implement new constraint: select between several string options
        * possibly be able to specify color palette?
    * be able to collapse & expand code sections [-] and [+] via /** directive **/

    * hover over keywords => inline documentation from:
        * http://processingjs.org/reference/textAlign_/

TEMPLATES:
    NOTE: all control-flow logic belongs in the processing code itself
    
    /** auto <type> **/
    /** auto color  **/
    
    /** restart_on_edit  **/
    /** no_restart_on_edit  **/
    
    /** range [ 0, 30 ] **/ /** endrange **/
    
    /** string  **/ /** endstring  **/
    /** color   **/ /** endcolor   **/
    /** float   **/ /** endfloat   **/
    /** int     **/ /** endint     **/
    /** boolean **/ /** endboolean **/
    /** char    **/ /** endchar    **/
    /** expr    **/ /** endexpr    **/
    
    /** int [ 0, 2 ] **/
    /** int [ 0, 3 ) **/
    
    /** float [ 0, 1 ) **/
    
    /** string function(s) { return s + ";" } **/
    /** string [ "s0", "s1", "s2" ] **/
    
    /** expr [ random(3, 5), 2 * random(-1, 50), (x ? 1.0 : -1.0) ] **/


TODO:
    * how to constrain alpha, hue, or etc. in /** color **/


OLD:
    /** switch **/
        /** case test0 }
            { break **/
        /** case test0 }
            { break **/
        /** default **/
            /** break **/
    /** endswitch **/

