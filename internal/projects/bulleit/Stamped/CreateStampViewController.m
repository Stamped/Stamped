//
//  CreateStampViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 7/25/11.
//  Copyright 2011 Stamped, Inc. All rights reserved.
//

#import "CreateStampViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "AccountManager.h"
#import "Entity.h"
#import "STNavigationBar.h"
#import "Stamp.h"
#import "UserImageView.h"
#import "Util.h"

static const CGFloat kMinContainerHeight = 204.0;

@interface CreateStampViewController ()
- (void)editorDoneButtonPressed:(id)sender;
- (void)dismissSelf;

@property (nonatomic, retain) UIButton* doneButton;
@end

@implementation CreateStampViewController

@synthesize scrollView = scrollView_;
@synthesize titleLabel = titleLabel_;
@synthesize detailLabel = detailLabel_;
@synthesize reasoningLabel = reasoningLabel_;
@synthesize categoryImageView = categoryImageView_;
@synthesize userImageView = userImageView_;
@synthesize ribbonedContainerView = ribbonedContainerView_;
@synthesize reasoningTextView = reasoningTextView_;
@synthesize doneButton = doneButton_;
@synthesize bottomToolbar = bottomToolbar_;
@synthesize shelfBackground = shelfBackground_;
@synthesize cancelButton = cancelButton_;
@synthesize spinner = spinner_;
@synthesize checkmarkButton = checkmarkButton_;
@synthesize creditTextField = creditTextField_;

- (id)initWithEntityObject:(Entity*)entityObject {
  self = [super initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    entityObject_ = [entityObject retain];
  }
  return self;
}

- (id)initWithEntityObject:(Entity*)entityObject creditedTo:(User*)user {
  self = [self initWithEntityObject:entityObject];
  if (self) {
    creditedUser_ = [user retain];
  }
  return self;
}

- (void)dealloc {
  [entityObject_ release];
  [creditedUser_ release];
  self.scrollView = nil;
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.reasoningLabel = nil;
  self.userImageView = nil;
  self.reasoningTextView = nil;
  self.ribbonedContainerView = nil;
  self.doneButton = nil;
  self.bottomToolbar = nil;
  self.shelfBackground = nil;
  self.spinner = nil;
  self.cancelButton = nil;
  self.checkmarkButton = nil;
  self.creditTextField = nil;
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
  User* currentUser = [AccountManager sharedManager].currentUser;
  self.userImageView.imageURL = currentUser.profileImageURL;
  scrollView_.contentSize = self.view.bounds.size;
  CAGradientLayer* backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.colors = [NSArray arrayWithObjects:
                               (id)[UIColor colorWithWhite:1.0 alpha:1.0].CGColor,
                               (id)[UIColor colorWithWhite:0.93 alpha:1.0].CGColor, nil];
  backgroundGradient.frame = self.view.bounds;
  [self.view.layer insertSublayer:backgroundGradient atIndex:0];
  [backgroundGradient release];
  
  ribbonedContainerView_.layer.shadowOpacity = 0.1;
  ribbonedContainerView_.layer.shadowOffset = CGSizeMake(0, 1);
  ribbonedContainerView_.layer.shadowRadius = 2;
  ribbonedContainerView_.layer.shadowPath =
      [UIBezierPath bezierPathWithRect:ribbonedContainerView_.bounds].CGPath;
  
  ribbonGradientLayer_ = [[CAGradientLayer alloc] init];
  CGFloat r1, g1, b1, r2, g2, b2;
  [Util splitHexString:currentUser.primaryColor toRed:&r1 green:&g1 blue:&b1];
  
  if (currentUser.secondaryColor) {
    [Util splitHexString:currentUser.secondaryColor toRed:&r2 green:&g2 blue:&b2];
  } else {
    r2 = r1;
    g2 = g1;
    b2 = b1;
  }
  ribbonGradientLayer_.colors =
      [NSArray arrayWithObjects:(id)[UIColor colorWithRed:r1 green:g1 blue:b1 alpha:0.75].CGColor,
                                (id)[UIColor colorWithRed:r2 green:g2 blue:b2 alpha:0.75].CGColor,
                                nil];
  ribbonGradientLayer_.frame = ribbonedContainerView_.bounds;
  ribbonGradientLayer_.startPoint = CGPointMake(0.0, 0.0);
  ribbonGradientLayer_.endPoint = CGPointMake(1.0, 1.0);
  [ribbonedContainerView_.layer insertSublayer:ribbonGradientLayer_ atIndex:0];
  [ribbonGradientLayer_ release];
  
  UIView* accessoryView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 44)];
  accessoryView.backgroundColor = [UIColor colorWithWhite:0.43 alpha:1.0];
  
  backgroundGradient = [[CAGradientLayer alloc] init];
  backgroundGradient.frame = CGRectMake(0, 1, 320, 43);
  backgroundGradient.colors = [NSArray arrayWithObjects:
      (id)[UIColor colorWithWhite:0.19 alpha:1.0].CGColor,
      (id)[UIColor colorWithWhite:0.33 alpha:1.0].CGColor, nil];
  [accessoryView.layer addSublayer:backgroundGradient];
  [backgroundGradient release];
  
  bottomToolbar_.layer.shadowPath = [UIBezierPath bezierPathWithRect:bottomToolbar_.bounds].CGPath;
  bottomToolbar_.layer.shadowOpacity = 0.2;
  bottomToolbar_.layer.shadowOffset = CGSizeMake(0, -1);
  bottomToolbar_.alpha = 0.5;

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
  [doneButton_ addTarget:self
                  action:@selector(editorDoneButtonPressed:)
        forControlEvents:UIControlEventTouchUpInside];
  
  titleLabel_.text = entityObject_.title;
  titleLabel_.font = [UIFont fontWithName:@"TitlingGothicFBComp-Regular" size:36];
  titleLabel_.textColor = [UIColor colorWithWhite:0.3 alpha:1.0];

  CGSize stringSize = [titleLabel_.text sizeWithFont:titleLabel_.font
                                            forWidth:CGRectGetWidth(titleLabel_.frame)
                                       lineBreakMode:titleLabel_.lineBreakMode];
  stampLayer_ = [[CALayer alloc] init];
  stampLayer_.frame = CGRectMake(15 + stringSize.width - (46 / 2),
                                11 - (46 / 2),
                                46, 46);
  stampLayer_.contents = (id)[AccountManager sharedManager].currentUser.stampImage.CGImage;
  stampLayer_.transform = CATransform3DMakeScale(15.0, 15.0, 1.0);
  stampLayer_.opacity = 0.0;
  [scrollView_.layer insertSublayer:stampLayer_ above:titleLabel_.layer];
  [stampLayer_ release];
  
  detailLabel_.text = entityObject_.subtitle;
  detailLabel_.textColor = [UIColor colorWithWhite:0.6 alpha:1.0];

  reasoningLabel_.textColor = [UIColor colorWithWhite:0.75 alpha:1.0];
  categoryImageView_.image = entityObject_.categoryImage;

  if (creditedUser_)
    creditTextField_.text = creditedUser_.screenName;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.scrollView = nil;
  self.titleLabel = nil;
  self.detailLabel = nil;
  self.categoryImageView = nil;
  self.reasoningLabel = nil;
  self.userImageView = nil;
  self.reasoningTextView = nil;
  self.ribbonedContainerView = nil;
  self.doneButton = nil;
  self.bottomToolbar = nil;
  self.shelfBackground = nil;
  self.spinner = nil;
  self.cancelButton = nil;
  self.checkmarkButton = nil;
  self.creditTextField = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

#pragma mark - UITextViewDelegate Methods.

- (void)textViewDidChange:(UITextView*)textView {
  if (textView != reasoningTextView_)
    return;

  reasoningLabel_.hidden = reasoningTextView_.hasText;
  CGSize stringSize = reasoningTextView_.contentSize;
  CGRect frame = ribbonedContainerView_.frame;
  frame.size.height = fmaxf(kMinContainerHeight, stringSize.height + 100);
  [UIView animateWithDuration:0.2 animations:^{
    ribbonedContainerView_.frame = frame;
    ribbonGradientLayer_.frame = ribbonedContainerView_.bounds;
    scrollView_.contentInset = UIEdgeInsetsMake(0, 0, 40, 0);
  }];
  scrollView_.contentSize = CGSizeMake(CGRectGetWidth(self.view.frame),
      CGRectGetHeight(self.view.frame) + (CGRectGetHeight(frame) - kMinContainerHeight));
  NSUInteger curPosition = reasoningTextView_.selectedRange.location;
  if (curPosition == reasoningTextView_.text.length) {
    [scrollView_ setContentOffset:CGPointMake(0, (CGRectGetHeight(frame) - kMinContainerHeight) + 40) animated:YES];
  }
}

#pragma mark - UITextFieldDelegate Methods.

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  if (textField != creditTextField_)
    return;
  
  [UIView animateWithDuration:0.2 animations:^{
    self.scrollView.contentInset =
      UIEdgeInsetsMake(0, 0, CGRectGetMaxY(ribbonedContainerView_.frame) - 50, 0);
    [self.scrollView setContentOffset:CGPointMake(0, CGRectGetMaxY(ribbonedContainerView_.frame) - 50) animated:YES];
  }];
}

- (void)textFieldDidEndEditing:(UITextField*)textField {
  if (textField != creditTextField_)
    return;
  [UIView animateWithDuration:0.2 animations:^{
    self.scrollView.contentInset = UIEdgeInsetsZero;
  }];
  [self.scrollView setContentOffset:CGPointZero animated:YES];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  if (textField != creditTextField_)
    return YES;
  
  [textField resignFirstResponder];
  return NO;
}

#pragma mark - Actions.

- (IBAction)backOrCancelButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

- (IBAction)saveStampButtonPressed:(id)sender {
  [spinner_ startAnimating];
  cancelButton_.enabled = NO;
  checkmarkButton_.enabled = NO;
  RKObjectManager* objectManager = [RKObjectManager sharedManager];
  RKObjectMapping* stampMapping = [objectManager.mappingProvider mappingForKeyPath:@"Stamp"];
  RKObjectLoader* objectLoader = [objectManager objectLoaderWithResourcePath:@"/stamps/create.json" delegate:self];
  objectLoader.method = RKRequestMethodPOST;
  objectLoader.objectMapping = stampMapping;
  NSString* credit = [creditTextField_.text stringByReplacingOccurrencesOfString:@" " withString:@""];
  objectLoader.params = [NSDictionary dictionaryWithObjectsAndKeys:
      reasoningTextView_.text, @"blurb",
      credit, @"credit",
      [AccountManager sharedManager].authToken.accessToken, @"oauth_token",
      entityObject_.entityID, @"entity_id", nil];
  [objectLoader send];
}

- (void)editorDoneButtonPressed:(id)sender {
  [reasoningTextView_ resignFirstResponder];
  [UIView animateWithDuration:0.2 animations:^{
    scrollView_.contentInset = UIEdgeInsetsZero;
  }];
  [scrollView_ setContentOffset:CGPointZero animated:YES];
}

- (void)dismissSelf {
  UIViewController* vc = nil;
  if ([self.navigationController respondsToSelector:@selector(presentingViewController)])
    vc = [self.navigationController presentingViewController];
  else
    vc = self.navigationController.parentViewController;
  if (vc && vc.modalViewController) {
    [vc dismissModalViewControllerAnimated:YES];
  } else {
    [self.navigationController popToRootViewControllerAnimated:YES];
  }
}

#pragma mark - RKObjectLoaderDelegate methods.

- (void)objectLoader:(RKObjectLoader*)objectLoader didLoadObjects:(NSArray*)objects {
	if (![objectLoader.resourcePath isEqualToString:@"/stamps/create.json"])
    return;

  Stamp* stamp = [objects objectAtIndex:0];
  [entityObject_ addStampsObject:stamp];
  [[NSNotificationCenter defaultCenter] postNotificationName:kStampWasCreatedNotification
                                                      object:stamp];
  
  [spinner_ stopAnimating];
  CGAffineTransform topTransform = CGAffineTransformMakeTranslation(0, -CGRectGetHeight(shelfBackground_.frame));
  CGAffineTransform bottomTransform = CGAffineTransformMakeTranslation(0, CGRectGetHeight(bottomToolbar_.frame));
  [UIView animateWithDuration:0.2
                   animations:^{ 
                     shelfBackground_.transform = topTransform;
                     bottomToolbar_.transform = bottomTransform;
                     checkmarkButton_.transform = bottomTransform;
                     cancelButton_.transform = bottomTransform;
                   }
                   completion:^(BOOL finished) {
                     [UIView animateWithDuration:0.3
                                           delay:0
                                         options:UIViewAnimationCurveEaseIn
                                      animations:^{
                                        stampLayer_.transform = CATransform3DIdentity;
                                        stampLayer_.opacity = 1.0;
                                      }
                                      completion:^(BOOL finished) {
                                        [self performSelector:@selector(dismissSelf)
                                                   withObject:nil
                                                   afterDelay:0.75];
                                      }];
                   }];
}

- (void)objectLoader:(RKObjectLoader*)objectLoader didFailWithError:(NSError*)error {
  [spinner_ stopAnimating];
  cancelButton_.enabled = YES;
  checkmarkButton_.enabled = YES;
  [UIView animateWithDuration:0.2
                   animations:^{
                     shelfBackground_.transform = CGAffineTransformIdentity;
                   }];
	NSLog(@"Hit error: %@", error);
}

@end
