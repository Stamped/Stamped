//
//  STActivityCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActivityCell.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "TTTAttributedLabel.h"
#import "STActionManager.h"
#import "STImageView.h"
#import "STStampedActions.h"

@interface STActivityCell () <TTTAttributedLabelDelegate>

+ (CGFloat)headerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)bodyHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)imagesHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)footerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (UIFont*)headerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (UIFont*)bodyFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (UIFont*)footerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (CGRect)headerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGRect)bodyBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGRect)imagesBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGRect)footerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

+ (CGFloat)topPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)bottomPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)xOffsetForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;
+ (CGFloat)textWidthForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope;

@property (nonatomic, readonly, retain) NSMutableArray* actions;
@property (nonatomic, readonly, retain) id<STActivity> activity;
@property (nonatomic, readonly, assign) STStampedAPIScope scope;

@end

@implementation STActivityCell

@synthesize actions = actions_;
@synthesize activity = activity_;
@synthesize scope = scope_;

- (void)addUserImagesForUsers:(NSArray<STUser>*)users inView:(UIView*)view {
  NSInteger imageLimit = MIN(4, self.activity.subjects.count);
  CGRect imagesBounds = [STActivityCell imagesBoundsForActivity:self.activity andScope:self.scope];
  for (NSInteger i = 0; i < imageLimit; i++) {
    id<STUser> subjectUser = [self.activity.subjects objectAtIndex:i];
    UIView* imageView = [Util profileImageViewForUser:subjectUser withSize:STProfileImageSize46];
    [Util reframeView:imageView withDeltas:CGRectMake(imagesBounds.origin.x + 51 * i, imagesBounds.origin.y, 0, 0)];
    [view addSubview:imageView];
    UIView* imageButton = [Util tapViewWithFrame:imageView.frame target:self selector:@selector(userImageClicked:) andMessage:subjectUser];
    [view addSubview:imageButton];
  }
}

- (void)addAttributedText:(NSString*)text 
                    frame:(CGRect)frame 
                     font:(UIFont*)font 
                    color:(UIColor*)color
               references:(NSArray<STActivityReference>*)references 
                   toView:(UIView*)view {
  TTTAttributedLabel* bodyView = [[[TTTAttributedLabel alloc] initWithFrame:frame] autorelease];
  bodyView.delegate = self;
  bodyView.userInteractionEnabled = YES;
  bodyView.textColor = color;
  bodyView.font = font;
  bodyView.dataDetectorTypes = UIDataDetectorTypeLink;
  bodyView.lineBreakMode = UILineBreakModeWordWrap;
  bodyView.text = text;
  if (references.count > 0) { 
    NSMutableDictionary* linkAttributes = [NSMutableDictionary dictionary];
    CTFontRef font = CTFontCreateWithName((CFStringRef)@"Helvetica-Bold", 12, NULL);
    [linkAttributes setValue:(id)font forKey:(NSString*)kCTFontAttributeName];
    CFRelease(font);
    bodyView.linkAttributes = [NSDictionary dictionaryWithDictionary:linkAttributes];
    for (id<STActivityReference> reference in references) {
      if (reference.indices.count == 2) {
        NSInteger start = [[reference.indices objectAtIndex:0] integerValue];
        NSInteger end = [[reference.indices objectAtIndex:1] integerValue];
        NSRange range = NSMakeRange(start, end-start);
        NSString* key;
        if (reference.action) {
          key = [NSString stringWithFormat:@"%d", self.actions.count];
          [self.actions addObject:reference.action];
        }
        else {
          key = @"-1";
        }
        [bodyView addLinkToURL:[NSURL URLWithString:key] withRange:range];
      }
    }
  }
  [view addSubview:bodyView];
}

- (id)initWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:@"test"];
  if (self) {
    actions_ = [[NSMutableArray alloc] init];
    activity_ = [activity retain];
    scope_ = scope;
    self.accessoryType = UITableViewCellAccessoryNone;
    CGFloat height = [STActivityCell heightForCellWithActivity:activity andScope:scope];
    UIView* view = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, [Util fullscreenFrame].size.width, height)] autorelease];
    if (activity.image) {
      STImageView* imageView = [[[STImageView alloc] initWithFrame:CGRectMake(
                                                                              ([STActivityCell xOffsetForActivity:activity andScope:scope] - STProfileImageSize31)/2,
                                                                              8,
                                                                              31,
                                                                              31)] autorelease];
      imageView.imageURL = activity.image;
      [view addSubview:imageView];
    }
    /*
     if (scope == STStampedAPIScopeYou) {
     
     }
     else {
     if (activity.subjects.count > 0) {
     id<STUser> subject = [activity.subjects objectAtIndex:0];
     UIView* imageView = [Util profileImageViewForUser:subject withSize:STProfileImageSize31];
     [Util reframeView:imageView withDeltas:CGRectMake(([STActivityCell xOffsetForActivity:activity andScope:scope] - STProfileImageSize31)/2, 8, 0, 0)];
     [view addSubview:imageView];
     }
     }
     */
    if (activity.header) {
      CGRect headerBounds = [STActivityCell headerBoundsForActivity:activity andScope:scope];
      CGRect headerFrame = headerBounds;
      headerFrame.size.height = [STActivityCell headerHeightForActivity:activity andScope:scope];
      [self addAttributedText:activity.header 
                        frame:headerFrame 
                         font:[STActivityCell headerFontForActivity:self.activity andScope:self.scope] 
                        color:[UIColor stampedGrayColor]
                   references:activity.headerReferences 
                       toView:view]; 
    }
    if (activity.body) {
      CGRect bodyBounds = [STActivityCell bodyBoundsForActivity:activity andScope:scope];
      CGRect bodyFrame = bodyBounds;
      bodyFrame.size.height = [STActivityCell bodyHeightForActivity:activity andScope:scope];
      [self addAttributedText:activity.body 
                        frame:bodyFrame 
                         font:[STActivityCell bodyFontForActivity:activity andScope:scope] 
                        color:[UIColor stampedDarkGrayColor]
                   references:activity.bodyReferences 
                       toView:view];
    }
    CGRect footerBounds = [STActivityCell footerBoundsForActivity:activity andScope:scope];
    UIView* dateView = [Util viewWithText:[Util shortUserReadableTimeSinceDate:activity.created] 
                                     font:[STActivityCell footerFontForActivity:activity andScope:scope]
                                    color:[UIColor stampedLightGrayColor]
                                     mode:UILineBreakModeClip
                               andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)];
    [Util reframeView:dateView withDeltas:CGRectMake(footerBounds.origin.x, footerBounds.origin.y, 0, 0)];
    [view addSubview:dateView];
    if (scope == STStampedAPIScopeYou) {
      if (activity.subjects.count > 1) {
        [self addUserImagesForUsers:activity.subjects inView:view];
      }
    }
    else {
      if (activity.objects.users.count > 1) {
      }
      else if (activity.subjects.count > 1) {
        [self addUserImagesForUsers:activity.subjects inView:view];
      }
    }
    if (activity.footer) {
      footerBounds.origin.x = CGRectGetMaxX(dateView.frame) + 5;
      footerBounds.size.width -= footerBounds.origin.x - dateView.frame.origin.x;
      UIView* footerView = [Util viewWithText:activity.footer
                                         font:[STActivityCell footerFontForActivity:activity andScope:scope]
                                        color:[UIColor stampedLightGrayColor]
                                         mode:UILineBreakModeWordWrap
                                   andMaxSize:footerBounds.size];
      [Util reframeView:footerView withDeltas:CGRectMake(footerBounds.origin.x, footerBounds.origin.y, 0, 0)];
      [view addSubview:footerView];
    }
    [self.contentView addSubview:view];
  }
  return self;
}

- (void)dealloc
{
  [actions_ release];
  [activity_ release];
  [super dealloc];
}

- (void)userImageClicked:(id<STUser>)user {
  STActionContext* context = [STActionContext context];
  context.user = user;
  id<STAction> action = [STStampedActions actionViewUser:user.userID withOutputContext:context];
  [[STActionManager sharedActionManager] didChooseAction:action withContext:context];
}

- (void)attributedLabel:(TTTAttributedLabel*)label didSelectLinkWithURL:(NSURL*)url {
  NSLog(@"url:%@",url);
  NSString* string = [url absoluteString];
  if (![string isEqualToString:@"-1"]) {
    id<STAction> action = [self.actions objectAtIndex:[string integerValue]];
    [[STActionManager sharedActionManager] didChooseAction:action withContext:[STActionContext context]];
  }
}

- (void)setSelected:(BOOL)selected animated:(BOOL)animated
{
  [super setSelected:selected animated:animated];
}

+ (CGFloat)heightForCellWithActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  CGFloat height = 0;
  height += [STActivityCell topPaddingForActivity:activity andScope:scope];
  height += [STActivityCell headerHeightForActivity:activity andScope:scope];
  height += [STActivityCell bodyHeightForActivity:activity andScope:scope];
  height += [STActivityCell imagesHeightForActivity:activity andScope:scope];
  height += [STActivityCell footerHeightForActivity:activity andScope:scope];
  height += [STActivityCell bottomPaddingForActivity:activity andScope:scope];
  return MAX(height,50);
}

+ (CGFloat)headerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (activity.header) {
    CGSize size = [Util sizeWithText:activity.header 
                                font:[STActivityCell headerFontForActivity:activity andScope:scope]
                                mode:UILineBreakModeWordWrap
                          andMaxSize:[STActivityCell headerBoundsForActivity:activity andScope:scope].size];
    return size.height;
  }
  else {
    return 0;
  }
}

+ (CGFloat)bodyHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (activity.body) {
    return [Util sizeWithText:activity.body 
                         font:[STActivityCell bodyFontForActivity:activity andScope:scope]
                         mode:UILineBreakModeWordWrap
                   andMaxSize:[STActivityCell bodyBoundsForActivity:activity andScope:scope].size].height;
  }
  else {
    return 0;
  }
}

+ (CGFloat)imagesHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (scope == STStampedAPIScopeYou) {
    if (activity.subjects.count > 1) {
      return 51;
    }
    else {
      return 0;
    }
  }
  else {
    if (activity.objects.users.count > 1) {
      return 51;
    }
    else if (activity.subjects.count > 1) {
      return 51;
    }
    else {
      return 0;
    }
  }
}

+ (CGFloat)footerHeightForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [Util sizeWithText:@"Test" 
                       font:[STActivityCell footerFontForActivity:activity andScope:scope] 
                       mode:UILineBreakModeTailTruncation 
                 andMaxSize:CGSizeMake(CGFLOAT_MAX, CGFLOAT_MAX)].height;
}

+ (UIFont*)headerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  if (activity.body) {
    return [UIFont stampedFontWithSize:12];
  }
  else {
    return [UIFont stampedFontWithSize:14];
  }
}

+ (UIFont*)bodyFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [UIFont stampedFontWithSize:12];
}

+ (UIFont*)footerFontForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [UIFont stampedFontWithSize:10];
}

+ (CGRect)headerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return CGRectMake([STActivityCell xOffsetForActivity:activity andScope:scope],
                    [STActivityCell topPaddingForActivity:activity andScope:scope], 
                    [STActivityCell textWidthForActivity:activity andScope:scope],
                    CGFLOAT_MAX);
}

+ (CGRect)bodyBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return CGRectMake([STActivityCell xOffsetForActivity:activity andScope:scope],
                    [STActivityCell headerBoundsForActivity:activity andScope:scope].origin.y + [STActivityCell headerHeightForActivity:activity andScope:scope], 
                    [STActivityCell textWidthForActivity:activity andScope:scope],
                    CGFLOAT_MAX);
}

+ (CGRect)imagesBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return CGRectMake([STActivityCell xOffsetForActivity:activity andScope:scope],
                    [STActivityCell bodyBoundsForActivity:activity andScope:scope].origin.y + [STActivityCell bodyHeightForActivity:activity andScope:scope], 
                    [STActivityCell textWidthForActivity:activity andScope:scope],
                    CGFLOAT_MAX);
}
+ (CGRect)footerBoundsForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return CGRectMake([STActivityCell xOffsetForActivity:activity andScope:scope],
                    [STActivityCell heightForCellWithActivity:activity andScope:scope] - ( [STActivityCell bottomPaddingForActivity:activity andScope:scope] + [STActivityCell footerHeightForActivity:activity andScope:scope] ), 
                    [STActivityCell textWidthForActivity:activity andScope:scope],
                    CGFLOAT_MAX);
}

+ (CGFloat)topPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return 5;
}

+ (CGFloat)bottomPaddingForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [STActivityCell topPaddingForActivity:activity andScope:scope];
}

+ (CGFloat)xOffsetForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return 60;
}

+ (CGFloat)textWidthForActivity:(id<STActivity>)activity andScope:(STStampedAPIScope)scope {
  return [Util fullscreenFrame].size.width - ( [STActivityCell xOffsetForActivity:activity andScope:scope] + 20 );
}

@end
