//
//  CreateStampDetailViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreateStampDetailViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "Entity.h"
#import "STNavigationBar.h"
#import "UserImageView.h"

@interface CreateStampDetailViewController ()
@property (nonatomic, retain) UIButton* doneButton;
@end

@implementation CreateStampDetailViewController

@synthesize titleLabel = titleLabel_;
@synthesize detailLabel = detailLabel_;
@synthesize reasoningLabel = reasoningLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize navigationBar = navigationBar_;
@synthesize userImageView = userImageView_;
@synthesize ribbonedContainerView = ribbonedContainerView_;
@synthesize reasoningTextView = reasoningTextView_;
@synthesize doneButton = doneButton_;

- (id)initWithEntityObject:(Entity*)entityObject {
  self = [super initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entityObject retain];
  }
  return self;
}

- (void)dealloc {
  [entityObject_ release];
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.navigationBar = nil;
  self.reasoningLabel = nil;
  self.userImageView = nil;
  self.reasoningTextView = nil;
  self.ribbonedContainerView = nil;
  self.doneButton = nil;
  [super dealloc];
}

- (void)didReceiveMemoryWarning {
  // Releases the view if it doesn't have a superview.
  [super didReceiveMemoryWarning];
  
  // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  [super viewDidLoad];
  navigationBar_.hideLogo = YES;

  self.reasoningTextView.hidden = YES;
  UIView* accessoryView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)];
  accessoryView.backgroundColor = [UIColor colorWithWhite:0.43 alpha:1.0];
  CAGradientLayer* backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.frame = CGRectMake(0, 1, 320, 43);
  backgroundGradient.colors = [NSArray arrayWithObjects:
      (id)[UIColor colorWithWhite:0.19 alpha:1.0].CGColor,
      (id)[UIColor colorWithWhite:0.33 alpha:1.0].CGColor, nil];
  [accessoryView.layer addSublayer:backgroundGradient];
  [backgroundGradient release];
  self.doneButton = [UIButton buttonWithType:UIButtonTypeCustom];
  self.doneButton.frame = CGRectMake(248, 5, 71, 36);
  UIImage* bg = [[UIImage imageNamed:@"done_button_bg"] stretchableImageWithLeftCapWidth:0 topCapHeight:0];
  [self.doneButton setImage:bg forState:UIControlStateNormal];
  self.doneButton.contentMode = UIViewContentModeScaleToFill;
  self.doneButton.layer.masksToBounds = YES;
  self.doneButton.layer.cornerRadius = 5;
  [accessoryView addSubview:self.doneButton];
  self.reasoningTextView.inputAccessoryView = accessoryView;
  [accessoryView release];
  
  titleLabel_.text = entityObject_.title;
  titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:36];
  titleLabel_.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];
  
  detailLabel_.text = entityObject_.subtitle;
  detailLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];
  
  reasoningLabel_.textColor = [UIColor colorWithWhite:0.75 alpha:1.0];
  reasoningLabel_.backgroundColor = [UIColor clearColor];
  
  categoryImageView_.image = entityObject_.categoryImage;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.navigationBar = nil;
  self.reasoningLabel = nil;
  self.userImageView = nil;
  self.reasoningTextView = nil;
  self.ribbonedContainerView = nil;
  self.doneButton = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (void)textViewDidChange:(UITextView*)textView {
  reasoningLabel_.hidden = reasoningTextView_.text.length > 0;
}

- (IBAction)reasoningTextPressed:(id)sender {
  reasoningTextView_.hidden = NO;
  [reasoningTextView_ becomeFirstResponder];
}

- (IBAction)backButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

@end
