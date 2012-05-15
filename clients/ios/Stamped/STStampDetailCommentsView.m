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
#import "STRippleBar.h"
#import "STProfileViewController.h"
#import "STPreviewsView.h"

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
    UIView* imageView = [Util profileImageViewForUser:user withSize:size];
    [Util reframeView:imageView withDeltas:CGRectMake(_imagePaddingX, _imagePaddingY, 0, 0)];
    [self addSubview:imageView];
    UIView* imageButton = [Util tapViewWithFrame:imageView.frame target:self selector:@selector(userImageClicked:) andMessage:user];
    [self addSubview:imageButton];
    _userImage = [imageView retain];
  }
  return self;
}

- (void)userImageClicked:(id<STUser>)user {
  STProfileViewController* controller = [[[STProfileViewController alloc] initWithUserID:user.userID] autorelease];
  [[Util sharedNavigationController] pushViewController:controller animated:YES];
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

- (id)initWithStamp:(id<STStamp>)stamp andIndex:(NSInteger)index;

@property (nonatomic, readonly, copy) NSString* imageURL;

@end

@implementation STStampDetailBlurbView

@synthesize imageURL = imageURL_;

- (id)initWithStamp:(id<STStamp>)stamp andIndex:(NSInteger)index {
  id<STContentItem> item = [stamp.contents objectAtIndex:index];
  self = [super initWithUser:stamp.user created:item.created text:item.blurb andProfileImageSize:ProfileImageSize46];
  if (self) {
    if (item.images) {
      id<STImageList> imageList = [item.images objectAtIndex:0];
      if (imageList.sizes.count > 0) {
        id<STImage> image = [imageList.sizes objectAtIndex:0];
        if (image.width && image.height && image.url) {
          CGSize imageSize = CGSizeMake(image.width.integerValue * [Util legacyImageScale], image.height.integerValue * [Util legacyImageScale]);
          UIView* imageView = [Util imageViewWithURL:[NSURL URLWithString:image.url]
                                            andFrame:CGRectMake(0, 0, imageSize.width, imageSize.height)];
          imageView.frame = [Util centeredAndBounded:imageView.frame.size inFrame:CGRectMake(0, self.frame.size.height, self.frame.size.width, MIN(200,imageSize.height))];
          [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, imageView.frame.size.height + 10)];
          [self addSubview:imageView];
          [imageView addGestureRecognizer:[[UITapGestureRecognizer alloc] initWithTarget:self action:@selector(imageClicked:)]];
        }
      }
    }
    CGFloat previewHeight = [STPreviewsView previewHeightForStamp:stamp andMaxRows:2];
    if ( previewHeight > 0 && index == 0) {
      STPreviewsView* view = [[[STPreviewsView alloc] initWithStamp:stamp andMaxRows:2] autorelease];
      [Util reframeView:view withDeltas:CGRectMake(60, self.frame.size.height, 0, 0)];
      [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, previewHeight)];
      [self addSubview:view];
    }
    //TODO likes, credited, border
  }
  return self;
}

- (void)imageClicked:(id)notImportant {
  if (self.imageURL) {
    
  }
}

- (void)dealloc
{
  [imageURL_ release];
  [super dealloc];
}

@end

@interface STStampDetailCommentsView ()

@property (nonatomic, readonly, assign) NSInteger index;
@property (nonatomic, readonly, assign) STStampDetailCommentsViewStyle style;
@property (nonatomic, readwrite, retain) id<STStamp> stamp;

@end

@implementation STStampDetailCommentsView

@synthesize index = index_;
@synthesize style = style_;
@synthesize stamp = stamp_;
@synthesize delegate = delegate_;

- (void)setStamp:(id<STStamp>)stamp {
  if (!stamp_ || ![stamp_.modified isEqualToDate:stamp.modified]) {
    BOOL first = stamp_ == nil;
    [stamp_ autorelease];
    stamp_ = [stamp retain];
    CGFloat heightBefore = self.frame.size.height;
    for (UIView* view in [NSArray arrayWithArray:self.subviews]) {
      [view removeFromSuperview];
    }
    [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, -self.frame.size.height)];
    [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 2)];
    
    STRippleBar* topBar = [[[STRippleBar alloc] initWithPrimaryColor:stamp.user.primaryColor andSecondaryColor:stamp.user.secondaryColor isTop:YES] autorelease];
    [Util appendView:topBar toParentView:self];
    
    UIView* blurbView = [[[STStampDetailBlurbView alloc] initWithStamp:stamp andIndex:index_] autorelease];
    [Util appendView:blurbView toParentView:self];
    if (index == 0 || YES) {
      NSInteger limit = stamp.previews.comments.count > 3 ? 2 : stamp.previews.comments.count;
      for (NSInteger i = 0; i < limit; i++) {
        NSInteger index = limit - (i + 1);
        id<STComment> comment = [stamp.previews.comments objectAtIndex:index];
        [Util appendView:[[[STStampDetailBarView alloc] init] autorelease] toParentView:self];
        STStampDetailCommentView* commentView = [[[STStampDetailCommentView alloc] initWithComment:comment] autorelease];
        [Util appendView:commentView toParentView:self];
      }
    }
    STRippleBar* bottomBar = [[[STRippleBar alloc] initWithPrimaryColor:stamp.user.primaryColor andSecondaryColor:stamp.user.secondaryColor isTop:NO] autorelease];
    [Util appendView:bottomBar toParentView:self];
    [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, 2)];
    
    if (!first) {
      CGFloat heightDelta = self.frame.size.height - heightBefore;
      NSLog(@"%f,%f,%f", heightBefore, self.frame.size.height, heightDelta);
      [Util reframeView:self withDeltas:CGRectMake(0, 0, 0, -heightDelta)];
      self.clipsToBounds = YES;
      [self.delegate childView:self shouldChangeHeightBy:heightDelta overDuration:.25];
    }
  }
}

- (id)initWithStamp:(id<STStamp>)stamp index:(NSInteger)index style:(STStampDetailCommentsViewStyle)style andDelegate:(id<STViewDelegate>)delegate
{
  CGFloat width = _totalWidth;
  CGFloat padding_x = 5;
  self = [super initWithFrame:CGRectMake(padding_x, 5, width, 0)];
  if (self) {
    delegate_ = delegate;
    index_ = index;
    style_ = style;
    self.backgroundColor = [UIColor whiteColor];
    
    self.layer.shadowColor = [UIColor blackColor].CGColor;
    self.layer.shadowOpacity = .1;
    self.layer.shadowRadius = 3.0;
    self.layer.shadowOffset = CGSizeMake(0, 1);
    
    [self setStamp:stamp];
  }
  return self;
}

- (void)dealloc
{
  [stamp_ release];
  [super dealloc];
}

- (void)reloadStampedData {
  [[STStampedAPI sharedInstance] stampForStampID:self.stamp.stampID andCallback:^(id<STStamp> stamp, NSError *error, STCancellation *cancellation) {
    if (stamp) {
      self.stamp = stamp;
    }
  }];
}

@end
