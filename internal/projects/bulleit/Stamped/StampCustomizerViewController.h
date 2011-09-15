//
//  StampCustomizerViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 9/14/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface StampCustomizerViewController : UIViewController {
 @private
  CGFloat primaryRed_;
  CGFloat primaryGreen_;
  CGFloat primaryBlue_;
  CGFloat secondaryRed_;
  CGFloat secondaryGreen_;
  CGFloat secondaryBlue_;
  
  CGFloat primaryHue_;
  CGFloat primaryBrightness_;
  CGFloat secondaryHue_;
  CGFloat secondaryBrightness_;
}

@property (nonatomic, retain) IBOutlet UISlider* brightnessSlider;
@property (nonatomic, retain) IBOutlet UISlider* hueSlider;
@property (nonatomic, retain) IBOutlet UIImageView* stampImageView;
@property (nonatomic, retain) IBOutlet UIButton* primaryColorButton;
@property (nonatomic, retain) IBOutlet UIButton* secondaryColorButton;

- (IBAction)primaryColorButtonPressed:(id)sender;
- (IBAction)secondaryColorButtonPressed:(id)sender;
- (IBAction)cancelButtonPressed:(id)sender;
- (IBAction)doneButtonPressed:(id)sender;

@end
