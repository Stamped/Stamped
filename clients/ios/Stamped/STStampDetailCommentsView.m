//
//  STStampDetailCommentsView.m
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampDetailCommentsView.h"
#import "UserImageView.h"
#import "User.h"
#import "STActionManager.h"
#import "STStampedActions.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STImageView.h"
#import "STSimpleUser.h"
#import "AccountManager.h"
#import "STStampedAPI.h"

static const CGFloat _totalWidth = 310;
static const CGFloat _imagePaddingX = 8;
static const CGFloat _imagePaddingY = _imagePaddingX;

@interface STStampDetailBarView : UIView

@end

@implementation STStampDetailBarView

- (id)init {
  self = [super initWithFrame:CGRectMake(0, 0, _totalWidth, 1)];
  if (self) {
    self.backgroundColor = [UIColor colorWithWhite:.90 alpha:1];
  }
  return self;
}

@end

@interface STAStampDetailCommentView : UIView

- (id)initWithUser:(id<STUser>)user andProfileImageSize:(STProfileImageSize)size;

@property (nonatomic, readonly, retain) UIView* userImage;

@end

@implementation STAStampDetailCommentView

@synthesize userImage = _userImage;

- (id)initWithUser:(id<STUser>)user andProfileImageSize:(STProfileImageSize)size {
  self = [super initWithFrame:CGRectMake(0, 0, _totalWidth, size + 2 * _imagePaddingY)];
  if (self) {
    STImageView* imageView = [[[STImageView alloc] initWithFrame:CGRectMake(_imagePaddingX, _imagePaddingY, size, size)] autorelease];
    imageView.imageURL = [Util profileImageURLForUser:user withSize:STProfileImageSize31];
    [self addSubview:imageView];
    _userImage = [imageView retain];
  }
  return self;
}

- (void)dealloc
{
  [_userImage release];
  [super dealloc];
}

/*
 TODO
 - (void)userImageTapped:(id)button {
 STActionContext* context = [STActionContext context];
 id<STAction> action = [STStampedActions actionViewUser:self.user.userID withOutputContext:context];
 [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
 NSLog(@"action not enabled");
 }
 */

@end

@interface STAStampDetailCommentWithText : STAStampDetailCommentView

- (id)initWithUser:(id<STUser>)user 
           created:(NSDate*)created 
              text:(NSString*)text 
andProfileImageSize:(STProfileImageSize)size;

@property (nonatomic, readonly, retain) UIView* userNameView;
@property (nonatomic, readonly, retain) UIView* dateView;
@property (nonatomic, readonly, retain) UIView* blurbView;

@end

@implementation STAStampDetailCommentWithText

@synthesize userNameView = _userNameView;
@synthesize dateView = _dateView;
@synthesize blurbView = _blurbView;

- (id)initWithUser:(id<STUser>)user  
           created:(NSDate*)created 
              text:(NSString*)text 
andProfileImageSize:(STProfileImageSize)size {
  self = [super initWithUser:user andProfileImageSize:size];
  if (self) {
    CGFloat boundsX = CGRectGetMaxX(self.userImage.frame) + 5;
    CGFloat dateX = _totalWidth - 30;
    CGRect textBounds = CGRectMake( boundsX, self.userImage.frame.origin.y, dateX - boundsX , CGFLOAT_MAX);
    UIFont* userNameFont = size == STProfileImageSize31 ? [UIFont stampedBoldFontWithSize:14] : [UIFont stampedBoldFontWithSize:16];
    _userNameView = [[Util viewWithText:user.screenName 
                                   font:userNameFont 
                                  color:[UIColor stampedGrayColor] 
                                   mode:UILineBreakModeClip 
                             andMaxSize:textBounds.size] retain];
    _userNameView.frame = CGRectOffset(_userNameView.frame, textBounds.origin.x, textBounds.origin.y);
    [self addSubview:_userNameView];
    
    UIFont* dateFont = size == STProfileImageSize31 ? [UIFont stampedFontWithSize:12] : [UIFont stampedFontWithSize:14];
    _dateView = [[Util viewWithText:[Util shortUserReadableTimeSinceDate:created]
                               font:dateFont 
                              color:[UIColor stampedLightGrayColor] 
                               mode:UILineBreakModeClip 
                         andMaxSize:CGSizeMake(30, 25)] retain];
    _dateView.frame = CGRectOffset(_dateView.frame, dateX, textBounds.origin.y);
    [self addSubview:_dateView];
    textBounds.origin.y = CGRectGetMaxY(_userNameView.frame) + 2;
    
    
    _blurbView = [[Util viewWithText:(text ? text : @" ")
                                font:[UIFont stampedFontWithSize:14]  
                               color:[UIColor stampedDarkGrayColor] 
                                mode:UILineBreakModeWordWrap 
                          andMaxSize:textBounds.size] retain];
    _blurbView.frame = CGRectOffset(_blurbView.frame, textBounds.origin.x, textBounds.origin.y);
    [self addSubview:_blurbView];
    
    CGRect frame = self.frame;
    frame.size.height = MAX(CGRectGetMaxY(self.userImage.frame), CGRectGetMaxY(self.blurbView.frame))+5;
    self.frame = frame;
  }
  return self;
}

- (void)dealloc
{
  [_blurbView release];
  [_userNameView release];
  [_dateView release];
  [super dealloc];
}

@end

@interface STStampDetailCommentView : STAStampDetailCommentWithText

-(id)initWithComment:(id<STComment>)comment;

@end

@implementation STStampDetailCommentView

- (id)initWithComment:(id<STComment>)comment {
  self = [super initWithUser:comment.user 
                     created:comment.created 
                        text:comment.blurb
         andProfileImageSize:STProfileImageSize31];
  if (self) {
    //Nothing
  }
  return self;
}

@end

@interface STStampDetailBlurbView : STAStampDetailCommentWithText

- (id)initWithStamp:(id<STStamp>)stamp;

@end

@implementation STStampDetailBlurbView

- (id)initWithStamp:(id<STStamp>)stamp {
  self = [super initWithUser:stamp.user created:stamp.created text:stamp.blurb andProfileImageSize:ProfileImageSize46];
  if (self) {
    //TODO likes, credited, border
  }
  return self;
}

@end

@interface STStampDetailAddCommentView : STAStampDetailCommentView

@property (nonatomic, readonly, retain) UITextField* textField;

- (id)initWithStamp:(id<STStamp>)stamp;

- (void)send:(id)button;

@property (nonatomic, readonly, retain) id<STStamp> stamp;

@end

@implementation STStampDetailAddCommentView

@synthesize stamp = _stamp;
@synthesize textField = _textField;

- (id)initWithStamp:(id<STStamp>)stamp
{
  self = [super initWithUser:[STSimpleUser userFromLegacyUser:[AccountManager sharedManager].currentUser] andProfileImageSize:STProfileImageSize31];
  if (self) {
    _stamp = [stamp retain];
    CGRect buttonFrame = CGRectMake(0, self.userImage.frame.origin.y, 55, self.userImage.frame.size.height);
    buttonFrame.origin.x = _totalWidth - (buttonFrame.size.width + 5);
    UIButton* sendButton = [[[UIButton alloc] initWithFrame:buttonFrame] autorelease];
    [sendButton setBackgroundImage:[UIImage imageNamed:@"green_button_bg"] forState:UIControlStateNormal];
    [sendButton addTarget:self action:@selector(send:) forControlEvents:UIControlEventTouchUpInside];
    [sendButton setTitle:@"Send" forState:UIControlStateNormal];
    [self addSubview:sendButton];
    CGRect textFieldFrame = CGRectMake(CGRectGetMaxX(self.userImage.frame)+ 5, self.userImage.frame.origin.y, 0, self.userImage.frame.size.height);
    textFieldFrame.size.width = CGRectGetMinX(sendButton.frame) - ( textFieldFrame.origin.x + 5 );
    _textField = [[UITextField alloc] initWithFrame:textFieldFrame];
    _textField.backgroundColor = [UIColor colorWithWhite:0 alpha:.1];
    [self addSubview:_textField];
  }
  return self;
}

- (void)dealloc
{
  [_stamp release];
  [_textField release];
  [super dealloc];
}

- (void)send:(id)button {
  //TODO
  [[STStampedAPI sharedInstance] createCommentForStampID:self.stamp.stampID withBlurb:self.textField.text andCallback:^(id<STComment> comment, NSError *error) {
    if (comment) {
      self.textField.text = @"";
      [Util reloadStampedData];
    }
  }];
}

@end

@implementation STStampDetailCommentsView

@synthesize addCommentView = _addCommentView;

- (id)initWithStamp:(id<STStamp>)stamp andDelegate:(id<STViewDelegate>)delegate
{
  CGFloat width = _totalWidth;
  CGFloat padding_x = 5;
  self = [super initWithDelegate:delegate andFrame:CGRectMake(padding_x, 5, width, 0)];
  if (self) {
    UIView* blurbView = [[STStampDetailBlurbView alloc] initWithStamp:stamp];
    [self appendChildView:blurbView];
    for (id<STComment> comment in stamp.commentsPreview) {
      [self appendChildView:[[[STStampDetailBarView alloc] init] autorelease]];
      STStampDetailCommentView* commentView = [[[STStampDetailCommentView alloc] initWithComment:comment] autorelease];
      [self appendChildView:commentView];
    }
    [self appendChildView:[[[STStampDetailBarView alloc] init] autorelease]];
    STStampDetailAddCommentView* addCommentView = [[[STStampDetailAddCommentView alloc] initWithStamp:stamp] autorelease];
    [self appendChildView:addCommentView];
    _addCommentView = [addCommentView.textField retain];
    
    self.backgroundColor = [UIColor whiteColor];
    
    self.layer.shadowColor = [UIColor blackColor].CGColor;
    self.layer.shadowOpacity = .1;
    self.layer.shadowRadius = 3.0;
    self.layer.shadowOffset = CGSizeMake(0, 1);
  }
  return self;
}

- (void)dealloc
{
  [_addCommentView release];
  [super dealloc];
}

@end