//
//  STInboxViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STInboxViewController.h"
#import "STStampsView.h"
#import "STMultipleChoiceButton.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "Util.h"
#import "STRootMenuView.h"
#import "STMapViewController.h"
#import "STScopeSlider.h"
#import "STToolbarView.h"
#import "STStampsViewSource.h"
#import "STFriendsOfFriendsSource.h"
#import "STSuggestedSource.h"
#import "STUserSource.h"
#import "SearchEntitiesViewController.h"
#import <QuartzCore/QuartzCore.h>
#import "STSearchField.h"

@interface STInboxCategoryFilterView : UIView

- (id)initWithInboxController:(STInboxViewController*)controller;

@property (nonatomic, readonly, assign) STInboxViewController* controller;

@end

@interface STInboxCategoryButton : UIButton

@property (nonatomic, readwrite, retain) STInboxCategoryFilterView* categoryView;

@end


@interface STInboxViewController () <STScopeSliderDelegate>

- (void)categoryChanged:(NSString*)category;
- (void)updateSource;
- (void)updateCategoryImage;
- (void)configureQueryField;

@property (nonatomic, readonly, retain) STInboxCategoryButton* categoryButton;
@property (nonatomic, readonly, retain) UITableView* stampsView;
@property (nonatomic, readonly, retain) UITextField* queryField;
@property (nonatomic, readonly, retain) NSDictionary* inboxSources;
@property (nonatomic, readwrite, assign) STStampedAPIScope scope;
@property (nonatomic, readwrite, copy) NSString* category;
@property (nonatomic, readwrite, copy) NSString* query;

@end

@implementation STInboxCategoryFilterView

@synthesize controller = _controller;

- (id)initWithInboxController:(STInboxViewController *)controller
{
  CGFloat buttonHeight = 85;
  CGFloat buttonWidth = 100;
  CGFloat buttonXPadding = 7;
  CGFloat buttonYPadding = 10;
  CGFloat buttonX = 3;
  CGFloat buttonY = 10;
  self = [super initWithFrame:CGRectMake(0, 0, 320, (buttonY*2+buttonYPadding+2*buttonHeight))];
  if (self) {
    _controller = controller;
    NSArray* categories = [NSArray arrayWithObjects:
                           @"None",
                           @"Music",
                           @"Food",
                           @"Book",
                           @"Film",
                           @"Other",
                           nil];
    for (NSInteger r = 0; r < 2; r++) {
      for (NSInteger c = 0; c < 3; c++) {
        NSString* category = [categories objectAtIndex:r*3+c];
        CGRect buttonFrame = CGRectZero;
        buttonFrame.origin.x = buttonX + ( ( buttonWidth + buttonXPadding ) * c );
        buttonFrame.origin.y = buttonY + ( ( buttonHeight + buttonYPadding ) * r );
        buttonFrame.size.width = buttonWidth;
        buttonFrame.size.height = buttonHeight;
        UIButton* button = [[[UIButton alloc] initWithFrame:buttonFrame] autorelease];
        CALayer* layer = button.layer;
        layer.cornerRadius = 5.0;
        layer.borderColor =[UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.4].CGColor;
        layer.borderWidth = 1.0;
        layer.shadowColor = [UIColor blackColor].CGColor;
        layer.shadowOpacity = .1;
        layer.shadowRadius = 2.0;
        layer.shadowOffset = CGSizeMake(0, 1);
        
         CAGradientLayer* gradient = [CAGradientLayer layer];
         gradient.anchorPoint = CGPointMake(0, 0);
         gradient.position = CGPointMake(0, 0);
         gradient.bounds = layer.bounds;
         gradient.cornerRadius = 5.0;
         gradient.colors = [NSMutableArray arrayWithObjects:
         (id)[UIColor colorWithWhite:.95 alpha:1].CGColor,
         (id)[UIColor colorWithWhite:.85 alpha:1].CGColor,
         nil];
         [layer addSublayer:gradient];
        button.tag = r*3+c;
        [button addTarget:self action:@selector(choseCategory:) forControlEvents:UIControlEventTouchUpInside];
        //[button setTitle:category forState:UIControlStateNormal];
        CGRect titleBounds = CGRectMake(0, buttonHeight-40, buttonWidth, 40);
        UIView* title = [Util viewWithText:category
                                      font:[UIFont stampedBoldFontWithSize:14]
                                     color:[UIColor stampedDarkGrayColor]
                                      mode:UILineBreakModeWordWrap
                                andMaxSize:titleBounds.size];
        title.frame = [Util centeredAndBounded:title.frame.size inFrame:titleBounds];
        [button addSubview:title];
        
        category = [category lowercaseString];
        category = [category isEqualToString:@"none"] ? @"place" : category; //hack for getting around nil icon, need new asset
        NSString* imagePath = [NSString stringWithFormat:@"cat_icon_eDetail_%@", category];
        UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imagePath]] autorelease];
        imageView.frame = [Util centeredAndBounded:[Util size:imageView.frame.size withScale:2]
                                           inFrame:CGRectMake(0, 0, buttonWidth, buttonHeight-20)];
        [button addSubview:imageView];
        [self addSubview:button];
      }
    }
    self.backgroundColor = [UIColor colorWithWhite:.1 alpha:.7];
  }
  return self;
}

- (void)choseCategory:(UIButton*)button {
  NSArray* categories = [NSArray arrayWithObjects:
                         @"None",
                         @"Music",
                         @"Food",
                         @"Book",
                         @"Film",
                         @"Other",
                         nil];
  NSString* category = [categories objectAtIndex:button.tag];
  category = [category lowercaseString];
  category = [category isEqualToString:@"none"] ? nil : category;
  [self.controller categoryChanged:category];
}

@end

@implementation STInboxCategoryButton

@synthesize categoryView = _categoryView;

- (id)initWithFrame:(CGRect)frame
{
  self = [super initWithFrame:frame];
  if (self) {
    self.backgroundColor = [UIColor whiteColor];
    self.layer.cornerRadius = 5.0;
    self.layer.borderColor =[UIColor colorWithRed:.8 green:.8 blue:.8 alpha:.7].CGColor;
    self.layer.borderWidth = 1.0;
    self.layer.shadowColor = [UIColor blackColor].CGColor;
    self.layer.shadowOpacity = .05;
    self.layer.shadowRadius = 2.0;
    self.layer.shadowOffset = CGSizeMake(0, 1);
    
    /*
    CAGradientLayer* gradient = [CAGradientLayer layer];
    gradient.anchorPoint = CGPointMake(0, 0);
    gradient.position = CGPointMake(0, 0);
    gradient.bounds = self.layer.bounds;
    gradient.cornerRadius = 2.0;
    gradient.colors = [NSMutableArray arrayWithObjects:
                       (id)[UIColor colorWithRed:1.0 green:1.0 blue:1.0 alpha:.8].CGColor,
                       (id)[UIColor colorWithRed:.95 green:.95 blue:.95 alpha:.6].CGColor,
                       nil];
    [self.layer addSublayer:gradient];
     */
  }
  return self;
}

- (UIView*)inputView {
  return self.categoryView;
}

- (BOOL)canBecomeFirstResponder {
  return YES;
}

@end

@implementation STInboxViewController

@synthesize categoryButton = _categoryButton;
@synthesize stampsView = _stampsView;
@synthesize queryField = _queryField;
@synthesize inboxSources = _inboxSources;
@synthesize scope = _scope;
@synthesize category = _category;
@synthesize query = _query;

static STInboxViewController* _sharedInstance;

+ (void)initialize {
  _sharedInstance = [[STInboxViewController alloc] init];
}

+ (STInboxViewController*)sharedInstance {
  return _sharedInstance;
}

- (id)init
{
  self = [super init];
  if (self) {
    //pass
  }
  return self;
}

- (void)viewDidLoad
{
  [super viewDidLoad];
  // UIPickerView* picker = [[[UIPickerView alloc] initWithFrame:CGRectMake(0, 0, 320, 20)] autorelease];
  //picker.delegate = self;
  //picker.dataSource = self;
  //[self.scrollView appendChildView:picker];
  UIView* searchBar = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 40)] autorelease];
  //_categoryButton.titleLabel.textColor = [UIColor stampedDarkGrayColor];
  //_categoryButton.backgroundColor = [UIColor colorWithWhite:.7 alpha:.8];
  //[searchBar addSubview:_categoryButton];
  _queryField = [[STSearchField alloc] initWithFrame:CGRectMake(10, 5, 300, 30)];
  _queryField.placeholder = @"Search for stamps";
  _queryField.enablesReturnKeyAutomatically = NO;
  //_queryField.backgroundColor = [UIColor whiteColor];
  _queryField.delegate = self;
  [self configureQueryField];
  //_queryField.se
  [searchBar addSubview:_queryField];
  searchBar.backgroundColor = [UIColor colorWithWhite:.9 alpha:1];
  searchBar.layer.shadowRadius = 4;
  searchBar.layer.shadowOpacity = .2;
  searchBar.layer.shadowOffset = CGSizeMake(0, 2);
  searchBar.layer.shadowColor = [UIColor blackColor].CGColor;
  [self.scrollView appendChildView:searchBar];
  _stampsView = [[UITableView alloc] initWithFrame:CGRectMake(0, 0, 320, 323)];
  //view.backgroundColor = [UIColor redColor];
  self.scope = STStampedAPIScopeFriends;
  _inboxSources = [[NSDictionary dictionaryWithObjectsAndKeys:
                    [[[STStampsViewSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeFriends],
                    [[[STUserSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeYou],
                    [[[STFriendsOfFriendsSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeFriendsOfFriends],
                    [[[STSuggestedSource alloc] init] autorelease], [NSNumber numberWithInt:STStampedAPIScopeEveryone],
                    nil] retain];
  
  self.scrollView.scrollsToTop = NO;
  [self.scrollView appendChildView:_stampsView];
  //TODO improve shadow hack
  [searchBar removeFromSuperview];
  [self.scrollView addSubview:searchBar];
  
  self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Home"
                                                                            style:UIBarButtonItemStyleDone
                                                                           target:self 
                                                                           action:@selector(backButtonClicked:)] autorelease];
  self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"+"
                                                                             style:UIBarButtonItemStyleDone
                                                                            target:self 
                                                                            action:@selector(rightButtonClicked:)] autorelease];
  STScopeSlider* slider = [[[STScopeSlider alloc] initWithFrame:CGRectMake(45, 15, 230, 23)] autorelease];
  slider.delegate = self;
  STToolbarView* toolbar = [[[STToolbarView alloc] init] autorelease];
  [toolbar addSubview:slider];
  UIButton* mapButton = [[[UIButton alloc] initWithFrame:CGRectMake(275, 10, 34, 30)] autorelease];
  //mapButton.titleLabel.text = @"Map";
  [mapButton setImage:[UIImage imageNamed:@"nav_map_button"] forState:UIControlStateNormal];
  [mapButton addTarget:self action:@selector(mapButtonClicked:) forControlEvents:UIControlEventTouchUpInside];
  [toolbar addSubview:mapButton];
  _categoryButton = [[STInboxCategoryButton alloc] initWithFrame:CGRectMake(9, 10, 34, 30)];
  [self updateCategoryImage];
  _categoryButton.categoryView = [[[STInboxCategoryFilterView alloc] initWithInboxController:self] autorelease];
  //_categoryButton.backgroundColor = [UIColor redColor];
  [_categoryButton addTarget:self action:@selector(categoryButtonPressed:) forControlEvents:UIControlEventTouchUpInside];
  [toolbar addSubview:_categoryButton];
  [self setToolbar:toolbar withAnimation:NO];
  [self updateSource];
}

- (void)updateCategoryImage {
  NSString* category = self.category;
  category = category ? category : @"place"; //hack for getting around nil icon, need new asset
  NSString* imagePath = [NSString stringWithFormat:@"cat_icon_eDetail_%@", category];
  [_categoryButton setImage:[UIImage imageNamed:imagePath] forState:UIControlStateNormal];
}

-(void)configureQueryField {
}

- (void)backButtonClicked:(id)button {
  [[STRootMenuView sharedInstance] toggle];
}

- (void)categoryButtonPressed:(id)button {
  [button becomeFirstResponder];
}

- (void)rightButtonClicked:(id)button {
  UINavigationController* controller = [Util sharedNavigationController];
  [controller pushViewController:[[[SearchEntitiesViewController alloc] initWithNibName:@"SearchEntitiesViewController" bundle:nil] autorelease]
                        animated:YES];
}

- (void)mapButtonClicked:(id)button {
  UINavigationController* controller = [Util sharedNavigationController];
  [controller pushViewController:[[[STMapViewController alloc] init] autorelease] animated:YES];
}


- (void)viewDidUnload
{
  [super viewDidUnload];
  [_categoryButton release];
  [_stampsView release];
  [_queryField release];
}

- (void)categoryChanged:(id)category {
  [self.categoryButton resignFirstResponder];
  self.category = category;
  [self updateCategoryImage];
  [self updateSource];
}

- (void)scopeSlider:(STScopeSlider*)slider didChangeGranularity:(STStampedAPIScope)granularity {
  //TODO switch to new enum
  self.scope = granularity;
  [self updateSource];
}

- (void)reloadStampedData {
  [self updateSource];
}

- (void)updateSource {
  STGenericCollectionSlice* slice = [[[STGenericCollectionSlice alloc] init] autorelease];
  [slice retain];
  slice.offset = [NSNumber numberWithInt:0];
  slice.limit = [NSNumber numberWithInt:NSIntegerMax];
  slice.category = self.category;
  slice.sort = @"created";
  slice.query = self.query;
  if (slice.query) {
    slice.sort = @"relevance";
  }
  for (STStampsViewSource* old in [self.inboxSources allValues]) {
    old.table = nil;
  }
  STStampsViewSource* source = [self.inboxSources objectForKey:[NSNumber numberWithInt:self.scope]];
  source.table = self.stampsView;
  source.slice = slice;
}

#pragma mark - UITextFieldDelegate Methods.

- (BOOL)textField:(UITextField *)textField shouldChangeCharactersInRange:(NSRange)range replacementString:(NSString *)string {
  [Util executeOnMainThread:^{
    self.query = textField.text;
  }];
  return YES;
}

- (void)textFieldDidBeginEditing:(UITextField*)textField {
  //Override collapsing behavior
}

- (void)textFieldDidEndEditing:(UITextField *)textField {
  //Override collapsing behavior
  self.query = [textField.text isEqualToString:@""] ? nil : textField.text;
  [self updateSource];
}

- (BOOL)textFieldShouldReturn:(UITextField*)textField {
  [textField resignFirstResponder];
  return YES;
}

@end
