//
//  STStampCell.m
//  Stamped
//
//  Created by Landon Judkins on 4/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStampCell.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import "TTTAttributedLabel.h"
#import "STPreviewsView.h"
#import "STConfiguration.h"
#import "STBlockUIView.h"
#import <QuartzCore/QuartzCore.h>
#import "STImageCache.h"
#import "QuartzUtils.h"
#import "STSimpleStamp.h"

@implementation STStampCell

@synthesize username=_username;
@synthesize subcategory=_subcategory;
@synthesize title=_title;
@synthesize category=_category;
@synthesize identifier=_identifier;
@synthesize commentCount=_commentCount;

- (id)initWithStyle:(UITableViewCellStyle)style reuseIdentifier:(NSString *)reuseIdentifier {
  if ((self = [super initWithStyle:UITableViewCellStyleDefault reuseIdentifier:reuseIdentifier])) {
      
      self.accessoryType = UITableViewCellAccessoryNone;
      
      CGFloat originY = 10.0f;
      
      // user image view
      UIImageView *imageView = [[UIImageView alloc] initWithFrame:CGRectMake(11.0f, originY, 46.0f, 46.0f)];
      imageView.layer.shadowPath = [UIBezierPath bezierPathWithRect:imageView.bounds].CGPath;
      imageView.layer.shadowOffset = CGSizeMake(0.0f, 1.0f);
      imageView.layer.shadowRadius = 1.0f;
      imageView.layer.shadowOpacity = 0.2f;
      imageView.layer.borderColor = [UIColor whiteColor].CGColor;
      imageView.layer.borderWidth = 1.0f;
      [self addSubview:imageView];
      _userImageView = imageView;
      [imageView release];
      
      STBlockUIView *background = [[STBlockUIView alloc] initWithFrame:self.bounds];
      background.autoresizingMask = UIViewAutoresizingFlexibleWidth | UIViewAutoresizingFlexibleHeight;
      background.contentMode = UIViewContentModeRedraw;
      background.backgroundColor = [UIColor whiteColor];
      [self addSubview:background];
      [background setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
          
          CGContextSaveGState(ctx);
          CGContextAddRect(ctx, CGRectMake(rect.origin.x, rect.origin.y, rect.size.width, 3.0f));
          CGContextClip(ctx);
          drawGradient([UIColor colorWithRed:0.8941f green:0.8941f blue:0.8941f alpha:1.0f].CGColor, [UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, ctx);
          CGContextRestoreGState(ctx);

          drawGradientWithStartPoint([UIColor colorWithRed:1.0f green:1.0f blue:1.0f alpha:1.0f].CGColor, [UIColor colorWithRed:0.9494f green:0.9494f blue:0.9494f alpha:1.0f].CGColor, rect.size.height - 10.0f, ctx);
          
      }];
      self.selectedBackgroundView = background;
      [background release];
      
      // cell text
      STBlockUIView *view = [[STBlockUIView alloc] initWithFrame:CGRectMake(68, originY, 200, 70.0f)];
      view.backgroundColor = [UIColor whiteColor];
      [self addSubview:view];
      [view setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
         
          if (_title) {
              
              UIFont *font = [UIFont stampedTitleLightFontWithSize:35];
              CGSize size = [_title sizeWithFont:font];

              if (_stampImage) {
                  [_stampImage drawInRect:CGRectMake(floorf(size.width - 7), 19.0f, _stampImage.size.width, _stampImage.size.height)];
              }
              
              [[UIColor stampedBlackColor] setFill];
              size.width = MIN(rect.size.width - 6.0f, size.width);
              [_title drawInRect:CGRectMake(rect.origin.x, 18.0f, size.width, size.height) withFont:font lineBreakMode:UILineBreakModeTailTruncation];
          
          }

          if (_username && _subcategory) {
              [[UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f] setFill];
              UIFont *font = [UIFont boldSystemFontOfSize:10];
              CGSize size = [_username sizeWithFont:font];
              [_username drawInRect:CGRectMake(rect.origin.x, rect.origin.y, size.width, size.height) withFont:font lineBreakMode:UILineBreakModeTailTruncation];
              [_subcategory drawAtPoint:CGPointMake(size.width, rect.origin.y) withFont:[UIFont systemFontOfSize:10]];
          }
          
          if (_category) {
              if (_categoryImage) {
                  [_categoryImage drawAtPoint:CGPointMake(rect.origin.x, 56.0f)];
              }
              [[UIColor colorWithRed:0.6f green:0.6f blue:0.6f alpha:1.0f] setFill];
              [_category drawAtPoint:CGPointMake((_categoryImage!=nil) ? _categoryImage.size.width + 5.0f : 0.0f, 54.0f) withFont:[UIFont systemFontOfSize:11]];
          }

      }];
      _headerView = view;
      [view release];
      
      // date label
      UILabel *label = [[UILabel alloc] initWithFrame:CGRectZero];
      label.font = [UIFont systemFontOfSize:9];
      label.textColor = [UIColor colorWithRed:0.7490f green:0.7490f blue:0.7490f alpha:1.0f];
      label.backgroundColor = [UIColor whiteColor];
      [self addSubview:label];
      _dateLabel = label;
      [label release];
      
      STPreviewsView *previewsView = [[STPreviewsView alloc] initWithFrame:CGRectMake(70.0f, 95.0f, 0, 0)];
      [self addSubview:previewsView];
      _statsView = previewsView;
      [previewsView release];
      _statsView.hidden = YES;
      
      // comment count
      STBlockUIView *commentView = [[STBlockUIView alloc] initWithFrame:CGRectMake(0.0f, 0.0f, 200, 30.0f)];
      commentView.backgroundColor = [UIColor whiteColor];
      [self addSubview:commentView];
      [commentView setDrawingHanlder:^(CGContextRef ctx, CGRect rect) {
          
          CGFloat offset = 0.0f;
          if (_commentCount > 0) {
              [[UIImage imageNamed:@"stamp_cell_comment.png"] drawAtPoint:CGPointMake(0, 1.0f)];
              offset += 12.0f;
              if (!_hasMedia) {
                  [[UIColor colorWithPatternImage:[UIImage imageNamed:@"stamp_cell_text_bg.png"]] setFill];
                  NSString *comments = [NSString stringWithFormat:@"%i", _commentCount];
                  CGFloat width = [[NSString stringWithFormat:@"%i", self.commentCount] sizeWithFont:[UIFont systemFontOfSize:9]].width;
                  UIFont *font = [UIFont systemFontOfSize:9];
                  [comments drawInRect:CGRectMake(offset, -1.0f, width, font.lineHeight) withFont:font];
                  offset += (width+2.0f);
              }
          }
          
          if (_hasMedia) {
              [[UIImage imageNamed:@"stamp_cell_media.png"] drawAtPoint:CGPointMake(offset, 0.0f)];
          }
          
      }];
      [commentView release];
      _commentView = commentView;

  }
  return self;
}

- (void)dealloc {
    
    [_categoryImage release], _categoryImage=nil;
    [_category release], _category=nil;
    [_title release], _title = nil;
    [_username release], _username = nil;
    [_subcategory release], _subcategory = nil;
    [_stampImage release], _stampImage = nil;
    
    _statsView = nil;
    _dateLabel = nil;

    [super dealloc];
    
}

- (void)setupWithStamp:(id<STStamp>)stamp {

    [_category release], _category=nil;
    _category = [stamp.entity.subtitle copy];
        
    [_title release], _title = nil;
    _title = [stamp.entity.title copy];
    
    [_username release], _username = nil;
    _username = [stamp.user.screenName copy];
    
    [_subcategory release], _subcategory = nil;
    _subcategory =  [[NSString stringWithFormat:@" stamped a %@", stamp.entity.subcategory] copy];
    
    [_categoryImage release], _categoryImage=nil;
    _categoryImage = [[Util imageForCategory:stamp.entity.category] retain];
    
    [_stampImage release], _stampImage=nil;
    _stampImage = [[Util stampImageForUser:stamp.user withSize:STStampImageSize14] retain];
   
    _commentCount = [stamp.numComments integerValue];
    for (id obj in stamp.contents) {
        _hasMedia = [[obj images] count] > 0;
        if (_hasMedia) {
            break;
        }
    }
    
    // stats previews
    _statsView.hidden = ([STPreviewsView previewHeightForStamp:stamp andMaxRows:1] <= 0.0f);
    if (!_statsView.hidden) {
        [_statsView setupWithStamp:stamp maxRows:1];
    }
    
    CGRect frame = _commentView.frame;
    frame.size.width = 0.0f;
    frame.size.height = 10.0f;
    if (_hasMedia) {
        frame.size.width += 10.0f;
    }
    if (_commentCount > 0) {
        frame.size.width += 12.0f;
        if (!_hasMedia) {
            frame.size.width += [[NSString stringWithFormat:@"%i", self.commentCount] sizeWithFont:[UIFont systemFontOfSize:9]].width;
        }
    }
    frame.origin.x = ceilf(self.bounds.size.width-(frame.size.width+16.0f));
    frame.origin.y = _statsView.hidden ? self.bounds.size.height - 20.0f : _statsView.frame.origin.y - 29.0f;
    _commentView.frame = frame;
    
    [_headerView setNeedsDisplay];
    [_commentView setNeedsDisplay];
    
    // date
    _dateLabel.text = [Util userReadableTimeSinceDate:stamp.created];
    [_dateLabel sizeToFit];
    frame = _dateLabel.frame;
    frame.origin = CGPointMake(floorf(self.bounds.size.width - (frame.size.width+16.0f)), 12);
    _dateLabel.frame = frame;
    
    // user avatar
    _userImageView.image = nil;
    UIImage *cachedImage = [[STImageCache sharedInstance] cachedUserImageForUser:stamp.user size:STProfileImageSize46];
    if (cachedImage) {
        _userImageView.image = cachedImage;
    } else {
        [[STImageCache sharedInstance] userImageForUser:stamp.user size:STProfileImageSize46 andCallback:^(UIImage *image, NSError *error, STCancellation *cancellation) {
            if (_userImageView) {
                _userImageView.image = image;
            }
        }];
    }
    
}

+ (NSString*)cellIdentifier {
    return @"_inboxTableCell";
}

+ (CGFloat)heightForStamp:(id<STStamp>)stamp {
    CGFloat defaultHeight = 90.0f;
    if (stamp) {
         NSInteger count = stamp.previews.credits.count + stamp.previews.likes.count + stamp.previews.todos.count + stamp.previews.comments.count;
        if (count > 0) {
            defaultHeight += 45.0f;
        }
    }
    return defaultHeight;
}

+ (STCancellation*)prepareForStamp:(id<STStamp>)stamp withCallback:(void (^)(NSError* error, STCancellation* cancellation))block {
    NSArray* images = [STPreviewsView imagesForPreviewWithStamp:stamp andMaxRows:1];
    NSMutableArray* allImages = [NSMutableArray arrayWithObject:[Util profileImageURLForUser:stamp.user withSize:STProfileImageSize46]];
    [allImages addObjectsFromArray:images];
    return [STCancellation loadImages:allImages withCallback:block];
}

@end
