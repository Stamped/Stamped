//
//  STGalleryView.m
//  Stamped
//
//  Created by Landon Judkins on 3/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGalleryView.h"
#import "STImageView.h"
#import <QuartzCore/QuartzCore.h>
#import "Util.h"
#import "STPageControl.h"
#import "UIColor+Stamped.h"
#import "STViewContainer.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STActionManager.h"

static const CGFloat _padding_w = 10;
static const CGFloat _padding_h = 10;
static const CGFloat _captionHeight = 25;

@interface STGalleryView ()

@property (nonatomic, retain) STPageControl* pageControl;

@end

@interface STGalleryItemView : UIView

- (id)initWithFrame:(CGRect)frame image:(UIImage*)image text:(BOOL)text andGalleryItem:(id<STImageList>)item;

- (void)clicked:(id)message;

@property (nonatomic, retain) NSString* link;
@property (nonatomic, retain) NSString* linkType;
@property (nonatomic, retain) UILabel* caption;
@property (nonatomic, readonly, retain) id<STImageList> galleryItem;

@end

@implementation STGalleryView

@synthesize pageControl = pageControl_;

- (id)initWithGallery:(id<STGallery>)gallery images:(NSDictionary*)images andDelegate:(id<STViewDelegate>)delegate {
    
    self = [super initWithFrame:CGRectZero];
    if (self) {
        
        CGFloat maxHeight = 0;
        BOOL hasText = NO;
        CGFloat width = 230;
        for (id<STImageList> item in gallery.images) {
            if (item.sizes.count > 0) {
                id<STImage> firstImage = [item.sizes objectAtIndex:0];
                if (firstImage.url) {
                    UIImage* image = [images objectForKey:firstImage.url];
                    if (image) {
                        CGFloat height = image.size.height + 2 * _padding_h;
                        CGRect imageFrame = [Util centeredAndBounded:image.size inFrame:CGRectMake(0, 0, width, height)];
                        hasText = hasText || item.caption;
                        maxHeight = MAX(maxHeight, imageFrame.size.height);
                    }
                }
            }
        }
        if (hasText) {
            maxHeight += _captionHeight;
        }
        if (maxHeight > 320) {
            maxHeight = 320;
        }
        
        
        CGSize totalSize = CGSizeMake(width, maxHeight);
        
        UIScrollView* scrollView = [[UIScrollView alloc] initWithFrame:[Util centeredAndBounded:totalSize inFrame:CGRectMake(0, 0, 320, maxHeight)]];
        scrollView.pagingEnabled = YES;
        scrollView.scrollEnabled = YES;
        scrollView.clipsToBounds = NO;
        scrollView.delegate = self;
        NSInteger offset = 0;
        for (NSInteger i = 0; i < [images count]; i++) {
            id<STImageList> item = [gallery.images objectAtIndex:i];
            if (item.sizes.count > 0) {
                id<STImage> firstImage = [item.sizes objectAtIndex:0];
                UIImage* image = [images objectForKey:firstImage.url];
                STGalleryItemView* view = [[STGalleryItemView alloc] initWithFrame:CGRectMake(offset, 0, width, maxHeight) image:image text:hasText andGalleryItem:item];
                [scrollView addSubview:view];
                [view release];
                offset += width;
            }
        }
        self.pageControl = [[[STPageControl alloc] initWithFrame:CGRectMake(0, 0, 100, 20)] autorelease];
        self.pageControl.radius = 3;
        self.pageControl.defaultColor = [UIColor stampedLightGrayColor];
        self.pageControl.selectedColor = [UIColor stampedDarkGrayColor];
        self.pageControl.spacing = self.pageControl.radius*3.5;
        self.pageControl.numberOfPages = [images count];
        
        CGSize pageControlSize = [self.pageControl sizeForNumberOfPages:self.pageControl.numberOfPages];
        self.pageControl.frame = [Util centeredAndBounded:pageControlSize inFrame:CGRectMake(0, maxHeight, 320, pageControlSize.height)];
        
        scrollView.showsHorizontalScrollIndicator = NO;
        scrollView.showsVerticalScrollIndicator = NO;
        [self addSubview:self.pageControl];
        [scrollView setContentSize:CGSizeMake(offset, maxHeight)];
        [self addSubview:scrollView];
        [scrollView release];
        self.frame = CGRectMake(0, 0, 320, CGRectGetMaxY(self.pageControl.frame)+10);
        
    }
    return self;
}

- (void)dealloc {
    self.pageControl = nil;
    [super dealloc];
}
- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
}

- (void)scrollViewDidEndDecelerating:(UIScrollView *)scrollView {
    NSInteger page = floor(scrollView.contentOffset.x * 1.0 / scrollView.frame.size.width + .5);
    self.pageControl.currentPage = page;
    [self.pageControl setNeedsDisplay];
}
@end

@implementation STGalleryItemView

@synthesize link = link_;
@synthesize linkType = linkType_;
@synthesize caption = caption_;
@synthesize galleryItem = _galleryItem;

- (id)initWithFrame:(CGRect)frame image:(UIImage*)image text:(BOOL)text andGalleryItem:(id<STImageList>)item {
    self = [super initWithFrame:frame];
    if (self) {
        _galleryItem = [item retain];
        CGRect bounds = CGRectMake(_padding_w, _padding_h, frame.size.width - 2 * _padding_w, frame.size.height - 2 * _padding_h);
        if (text) {
            bounds.origin.y += _captionHeight;
            bounds.size.height -= _captionHeight;
        }
        CGRect imageFrame = [Util centeredAndBounded:image.size inFrame:bounds];
        if (text && item.caption) {
            bounds.origin.y = 0;
            bounds.size.height = _captionHeight;
            UIView* captionView = [Util viewWithText:item.caption 
                                                font:[UIFont stampedFontWithSize:12]
                                               color:[UIColor stampedDarkGrayColor]
                                                mode:UILineBreakModeTailTruncation
                                          andMaxSize:bounds.size];
            captionView.frame = [Util centeredAndBounded:captionView.frame.size inFrame:bounds];
            [self addSubview:captionView];
        }
        UIImageView* view = [[[UIImageView alloc] initWithFrame:imageFrame] autorelease];
        view.image = image;
        view.backgroundColor = [UIColor clearColor];
        [self addSubview:view];
        if (item.action) {
            UIView* tapTarget = [Util tapViewWithFrame:view.frame target:self selector:@selector(clicked:) andMessage:nil];
            [self addSubview:tapTarget];
        }
    }
    return self;
}

- (void)clicked:(id)message {
    [[STActionManager sharedActionManager] didChooseAction:self.galleryItem.action withContext:[STActionContext contextInView:self]];
}

- (void)dealloc {
    self.link = nil;
    self.linkType = nil;
    self.caption = nil;
    [_galleryItem release];
    [super dealloc];
}

@end
