//
//  PairedLabel.m
//  Stamped
//
//  Created by Jake Zien on 9/9/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "PairedLabel.h"

@implementation PairedLabel

@synthesize nameLabel   = nameLabel_;
@synthesize valueLabel  = valueLabel_;
@synthesize nameWidth   = nameWidth_;
@synthesize numberWidth = numberWidth_;

static const CGFloat kTextLabelGutterWidth = 20.f;
static const CGFloat kNumberLabelGutterWidth = 8.f;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
      nameWidth_ =  0.f;
      numberWidth_= 0.f;
    }
    return self;
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad
{
  [super viewDidLoad];
}

- (void)viewDidUnload
{
    [super viewDidUnload];
    // Release any retained subviews of the main view.
    // e.g. self.myOutlet = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation
{
    // Return YES for supported orientations
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)setNameWidth:(CGFloat)newWidth
{
  nameWidth_ = newWidth;

  CGRect frame = nameLabel_.frame;
  frame.size.width = nameWidth_;
  nameLabel_.frame = frame;
  
  frame = valueLabel_.frame;
  frame.size.width = CGRectGetWidth(self.view.frame) - CGRectGetWidth(nameLabel_.frame) - kTextLabelGutterWidth;
  frame.origin.x = CGRectGetMaxX(nameLabel_.frame) + kTextLabelGutterWidth;
  
  CGSize valueLabelSize = [valueLabel_.text sizeWithFont:valueLabel_.font 
                                       constrainedToSize:CGSizeMake(frame.size.width, HUGE_VAL)
                                           lineBreakMode:UILineBreakModeWordWrap];
  
  frame.size = valueLabelSize;

  if (valueLabelSize.height - 15.f > 0.f)
  {
    CGFloat newHeight = valueLabel_.frame.origin.y + valueLabelSize.height + 10.f;
    CGRect viewFrame = self.view.frame;
    viewFrame.size.height = newHeight;
    self.view.frame = viewFrame;
    
    frame.origin.y = 0.0;
  }
  
  valueLabel_.frame = frame;

}


- (void)setNumberWidth:(CGFloat)newWidth
{
  numberWidth_ = newWidth;
  
  CGRect frame = nameLabel_.frame;
  frame.size.width = numberWidth_;
  nameLabel_.frame = frame;
  nameLabel_.contentMode = UIViewContentModeBottomLeft;
  
  frame = valueLabel_.frame;
  frame.size.width = CGRectGetWidth(self.view.frame) - CGRectGetWidth(nameLabel_.frame) - kNumberLabelGutterWidth;
  frame.origin.x = CGRectGetMaxX(nameLabel_.frame) + kNumberLabelGutterWidth;
  
  CGSize valueLabelSize = [valueLabel_.text sizeWithFont:valueLabel_.font 
                                       constrainedToSize:CGSizeMake(frame.size.width, HUGE_VAL)
                                           lineBreakMode:UILineBreakModeWordWrap];
  frame.size.height = valueLabelSize.height;
  
  if (valueLabelSize.height - 15.f > 0.f)
  {
    CGFloat newHeight = valueLabel_.frame.origin.y + valueLabelSize.height + 10.f;
    CGRect viewFrame = self.view.frame;
    viewFrame.size.height = newHeight;
    self.view.frame = viewFrame;
    
    frame.origin.y = 0.0;
  }
  
  valueLabel_.frame = frame;
  
}



@end
