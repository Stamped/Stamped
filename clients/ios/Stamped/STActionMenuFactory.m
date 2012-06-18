//
//  STActionMenuFactory.m
//  Stamped
//
//  Created by Landon Judkins on 3/16/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STActionMenuFactory.h"
#import "Util.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STViewContainer.h"
#import <QuartzCore/QuartzCore.h>
#import "STActionManager.h"

@interface STSourceCell : UIView <STViewDelegateDependent>

- (id)initWithDelegate:(id<STViewDelegate>)delegate;

@property (nonatomic, retain) id<STSource> source;
@property (nonatomic, retain) NSString* action;
@property (nonatomic, readwrite, assign) id<STViewDelegate> delegate;
@property (nonatomic, readwrite, retain) STActionContext* context;

- (void)callback:(id)state;

@end

@implementation STActionMenuFactory

- (NSOperation*)createViewWithAction:(id<STAction>)action 
                             sources:(NSArray*)sources 
                          andContext:(STActionContext*)context 
                            forBlock:(void (^)(STViewCreator))callback {
  __block NSBlockOperation* operation = [[[NSBlockOperation alloc] init] autorelease];
  [operation addExecutionBlock:^{
    @try {
      @autoreleasepool {
        BOOL failed = NO;
        NSMutableArray* array = [NSMutableArray array];
        if (action) {
          for (id<STSource> source in sources) {
            @autoreleasepool {
              if ([operation isCancelled]) {
                failed = YES;
                break;
              }
              NSData* data = [NSData dataWithContentsOfURL:[NSURL URLWithString:source.icon]];
              UIImage* image = [UIImage imageWithData:data];
              if (image) {
                [array addObject:image];
              }
              else {
                image = [UIImage imageNamed:@"cat_icon_sDetail_other"];
                [array addObject:image];
              }
            }
          }
        }
        else {
          failed = YES;
        }
        if ([operation isCancelled]) {
          failed = YES;
        }
        if (failed || [array count] == 0) {
          dispatch_async(dispatch_get_main_queue(), ^{
            @autoreleasepool {
              callback(nil);
            }
          });
        }
        else {
          dispatch_async(dispatch_get_main_queue(), ^{
            @autoreleasepool {
              if ([operation isCancelled]) {
                callback(nil);
              }
              else {
                STViewCreator init = ^(id<STViewDelegate> delegate) {
                  CGFloat width = 294;
                  CGFloat cellHeight = 40;
                  STViewContainer* view = [[STViewContainer alloc] initWithDelegate:delegate andFrame:CGRectMake(13, 0, width, 0)];
                  CAGradientLayer* gradient = [CAGradientLayer layer];
                    gradient.contentsScale = [[UIScreen mainScreen] scale];
                  gradient.anchorPoint = CGPointMake(0, 0);
                  gradient.position = CGPointMake(0, 0);
                  gradient.cornerRadius = 4;
                  gradient.colors = [NSMutableArray arrayWithObjects:
                                     (id)[UIColor colorWithRed:1.0 green:1.0 blue:1.0 alpha:.8].CGColor,
                                     (id)[UIColor colorWithRed:.95 green:.95 blue:.95 alpha:.6].CGColor,
                                     nil];
                  [view.layer addSublayer:gradient];
                  view.backgroundColor = [UIColor whiteColor];
                  view.layer.cornerRadius = 4.0;
                  view.layer.borderColor =[UIColor colorWithRed:.35 green:.35 blue:.35 alpha:1].CGColor;
                  view.layer.borderWidth = 2.0;
                  view.layer.shadowColor = [UIColor blackColor].CGColor;
                  view.layer.shadowOpacity = .6;
                  view.layer.shadowRadius = 5.0;
                  view.layer.shadowOffset = CGSizeMake(0, 4);
                  
                  
                  UIImage* image = [UIImage imageNamed:@"eDetailBox_line"];
                  
                  for (NSInteger i = 0; i < [array count]; i++) {
                    UIImage* iconImage = [array objectAtIndex:i];
                    STSourceCell* cell = [[[STSourceCell alloc] initWithDelegate:delegate] autorelease];
                    cell.context = context;
                    cell.frame = CGRectMake(0, 0, width, cellHeight);
                    UIImageView* icon = [[UIImageView alloc] init];
                    icon.image = iconImage;
                    icon.frame = [Util centeredAndBounded:[Util size:iconImage.size withScale:[Util legacyImageScale]] inFrame:CGRectMake(0, 0, cellHeight, cellHeight)];
                    id<STSource> source = [sources objectAtIndex:i];
                    cell.action = action.type;
                    cell.source = source;
                    UIView* text = [Util viewWithText:source.name
                                                 font:[UIFont stampedBoldFontWithSize:14] 
                                                color:[UIColor stampedDarkGrayColor]
                                                 mode:UILineBreakModeClip
                                           andMaxSize:CGSizeMake(width, cellHeight)];
                    text.frame = CGRectMake(cellHeight, 0, text.frame.size.width, cellHeight);
                    
                    UIView* button = [Util tapViewWithFrame:cell.frame target:cell selector:@selector(callback:) andMessage:nil];
                    [cell addSubview:button];
                    
                    [cell addSubview:text];
                    [cell addSubview:icon];
                    [view appendChildView:cell];
                    if (i + 1 != [array count] ) {
                      UIImageView* bar = [[UIImageView alloc] initWithImage:image];
                      bar.backgroundColor = [UIColor clearColor];
                      [view appendChildView:bar];
                      [bar release];
                    }
                    [icon release];
                  }
                  gradient.frame = CGRectMake(0, 0, width, view.frame.size.height);
                  return view;
                };
                callback(init);
              }
            }
          });
        }
      }
    }
    @catch (NSException *exception) {
      NSLog(@"exception occurred! %@",exception);
      NSLog(@"%@",[NSThread callStackSymbols]);
    }
    @finally {
    }
  }];
  return operation;
}

@end

@implementation STSourceCell

@synthesize source = source_;
@synthesize action = action_;
@synthesize delegate = delegate_;
@synthesize context = context_;


- (id)initWithDelegate:(id<STViewDelegate>)delegate {
  self = [super init];
  if (self) {
    delegate_ = delegate;
    if (delegate && [delegate respondsToSelector:@selector(registerDependent:)]) {
      [delegate registerDependent:self];
    }
  }
  return self;
}

- (void)dealloc {
  self.source = nil;
  self.action = nil;
  self.context = nil;
  [super dealloc];
}

- (void)callback:(id)state {
  NSLog(@"testing");
  if (self.delegate && [self.delegate respondsToSelector:@selector(didChooseSource:forAction:)]) {
    [self.delegate didChooseSource:self.source forAction:self.action withContext:self.context];
  }
  else {
    [[STActionManager sharedActionManager] didChooseSource:self.source forAction:self.action withContext:self.context];
  }
}


@end
