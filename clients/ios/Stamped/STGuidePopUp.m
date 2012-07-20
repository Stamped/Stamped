//
//  STGuidePopUp.m
//  Stamped
//
//  Created by Landon Judkins on 7/14/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 ACTUALLY DECENT CODE
 */

#import "STGuidePopUp.h"
#import "Util.h"
#import "STRippleBar.h"
#import "STTextChunk.h"
#import "STChunksView.h"
#import "UIFont+Stamped.h"
#import "UIColor+Stamped.h"
#import "STPageControl.h"

static NSString* const _hasShownPopUpUserDefaultsKey = @"Guide.hasShownPopUp";

@interface STGuidePopUp () <UIScrollViewDelegate>

@property (nonatomic, readonly, retain) STPageControl* pageControl;

@end

@implementation STGuidePopUp

@synthesize pageControl = _pageControl;

- (id)init
{
    CGSize contentSize = CGSizeMake(290, 314);
    self = [super initWithFrame:[Util centeredAndBounded:contentSize inFrame:[Util fullscreenFrame]]];
    if (self) {
        UIView* contentView = self;
        self.backgroundColor = [UIColor whiteColor];
        UIView* topRipple = [[[STRippleBar alloc] initWithFrame:CGRectMake(0, 0, contentSize.width, STRippleBarHeight)
                                                andPrimaryColor:[STRippleBar grayColor]
                                              andSecondaryColor:[STRippleBar grayColor]
                                                          isTop:YES] autorelease];
        [contentView addSubview:topRipple];
        
        UIView* bottomRipple = [[[STRippleBar alloc] initWithFrame:CGRectMake(0, contentSize.height - STRippleBarHeight, contentSize.width, STRippleBarHeight)
                                                   andPrimaryColor:[STRippleBar grayColor]
                                                 andSecondaryColor:[STRippleBar grayColor]
                                                             isTop:NO] autorelease];
        [contentView addSubview:bottomRipple];
        
        
        //Use left alignment for ease of adding stars
        NSMutableArray* chunks = [NSMutableArray array];
        STChunk* titleStart = [STChunk chunkWithLineHeight:32 andWidth:contentSize.width];
        STTextChunk* titleChunk = [[[STTextChunk alloc] initWithPrev:titleStart
                                                                text:@"Welcome to The Guide."
                                                                font:[UIFont stampedTitleLightFontWithSize:32]
                                                               color:[UIColor stampedColorWithHex:@"262626"]
                                                             kerning:0] autorelease];
        CGFloat titlePadding = (contentSize.width - titleChunk.end) / 2;
        titleChunk.bottomLeft = CGPointMake(titlePadding, 13 * 4);
        [chunks addObject:titleChunk];
        
        //Use center alignment for flexibility
        STChunk* bodyStart = [STChunk chunkWithLineHeight:16 andWidth:contentSize.width];
        bodyStart.bottomLeft = CGPointMake(0, 20 * 4);
        UIFont* bodyFont = [UIFont stampedFontWithSize:13];
        NSAttributedString* bodyString = [Util attributedStringForString:@"A visual and personalized way\nto find the best new things to try.\nGet started."
                                                                    font:bodyFont
                                                                   color:[UIColor stampedColorWithHex:@"999999"]
                                                              lineHeight:16
                                                                  indent:0
                                                               alignment:kCTCenterTextAlignment
                                                         extraAttributes:[NSDictionary dictionary]];
        STChunk* bodyChunk = [[[STTextChunk alloc] initWithPrev:bodyStart
                                               attributedString:bodyString
                                                 andPrimaryFont:bodyFont] autorelease];
        [chunks addObject:bodyChunk];
        
        STChunksView* chunksView = [[[STChunksView alloc] initWithChunks:chunks] autorelease];
        chunksView.userInteractionEnabled = NO;
        [contentView addSubview:chunksView];
        
        CGFloat scrollContentOffset = 32 * 4;
        UIScrollView* scrollView = [[[UIScrollView alloc] initWithFrame:CGRectMake(0, 0, contentSize.width, contentSize.height)] autorelease];
        
        NSArray* pageContent = [NSArray arrayWithObjects:
                            [NSArray arrayWithObjects:
                             @"guide-welcome-map",
                             @"See a map of the best places\nto eat and drink.",
                             nil],
                            [NSArray arrayWithObjects:
                             @"guide-welcome-music",
                             @"Listen to the best songs and albums.",
                             nil],
                            [NSArray arrayWithObjects:
                             @"guide-welcome-movies",
                             @"Find the best TV shows and\nmovies to watch.",
                             nil],
                            [NSArray arrayWithObjects:
                             @"guide-welcome-books",
                             @"Learn about the best books to read.",
                             nil],
                            [NSArray arrayWithObjects:
                             @"guide-welcome-apps",
                             @"Download the most fun\nand useful apps.",
                             nil],
                            nil];
        for (NSInteger i = 0; i < pageContent.count; i++) {
            NSArray* items = [pageContent objectAtIndex:i];
            NSString* imageName = [items objectAtIndex:0];
            NSString* pageText = [items objectAtIndex:1];
            UIImageView* imageView = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:imageName]] autorelease];
            imageView.frame = [Util centeredAndBounded:imageView.frame.size 
                                               inFrame:CGRectMake(i * contentSize.width, scrollContentOffset + 4, contentSize.width, imageView.frame.size.height)];
            [scrollView addSubview:imageView];
            
            STChunk* pageTextStart = [STChunk chunkWithLineHeight:16 andWidth:contentSize.width];
            pageTextStart.bottomLeft = CGPointMake(i * contentSize.width, scrollContentOffset + 32 * 4);
            UIFont* pageFont = [UIFont stampedFontWithSize:13];
            NSAttributedString* formattedText = [Util attributedStringForString:pageText
                                                                           font:pageFont
                                                                          color:[UIColor stampedColorWithHex:@"262626"]
                                                                     lineHeight:pageTextStart.lineHeight
                                                                         indent:0 
                                                                      alignment:kCTCenterTextAlignment
                                                                extraAttributes:[NSDictionary dictionary]];
            STTextChunk* pageTextChunk = [[[STTextChunk alloc] initWithPrev:pageTextStart
                                                           attributedString:formattedText
                                                             andPrimaryFont:pageFont] autorelease];
            STChunksView* pageChunksView = [[[STChunksView alloc] initWithChunks:[NSArray arrayWithObject:pageTextChunk]] autorelease];
            [scrollView addSubview:pageChunksView];
        }
        scrollView.delegate = self;
        scrollView.pagingEnabled = YES;
        scrollView.showsHorizontalScrollIndicator = NO;
        scrollView.showsVerticalScrollIndicator = NO;
        scrollView.contentSize = CGSizeMake(contentSize.width * pageContent.count, scrollView.frame.size.height);
        
        [contentView addSubview:scrollView];
        
        
        STPageControl* pageControl = [[[STPageControl alloc] initWithFrame:CGRectMake(0, 0, 100, 20)] autorelease];
        pageControl.radius = 3;
        pageControl.defaultColor = [UIColor colorWithRed:175/255. green:202/255. blue:238/255. alpha:1];
        pageControl.selectedColor = [UIColor colorWithRed:53/255. green:125/255. blue:215/255. alpha:1];
        pageControl.spacing = pageControl.radius*3.5;
        pageControl.numberOfPages = pageContent.count;
        
        CGSize pageControlSize = [pageControl sizeForNumberOfPages:pageControl.numberOfPages];
        pageControl.frame = [Util centeredAndBounded:pageControlSize inFrame:CGRectMake(0, 280, contentSize.width, pageControlSize.height)];
        
        _pageControl = [pageControl retain];
        [contentView addSubview:_pageControl];
        
        UIImageView* sparkleImage = [[[UIImageView alloc] initWithImage:[UIImage imageNamed:@"left_menu_icon_guide"]] autorelease];
        [Util reframeView:sparkleImage withDeltas:CGRectMake(215, 15.5, 0, 0)];
        [contentView addSubview:sparkleImage];
        
        UIImage* closeImage = [UIImage imageNamed:@"welcome_popover_close.png"];
        CGSize closeSize = closeImage.size;
        UIButton *closeButton = [UIButton buttonWithType:UIButtonTypeCustom];
        closeButton.frame = CGRectMake(-closeSize.width/2, -closeSize.height/2, closeSize.width, closeSize.height);
        [closeButton addTarget:self action:@selector(close:) forControlEvents:UIControlEventTouchUpInside];
        [closeButton setImage:closeImage forState:UIControlStateNormal];
        [contentView addSubview:closeButton];
    }
    return self;
}

- (void)dealloc
{
    [_pageControl release];
    [super dealloc];
}

- (void)close:(id)notImportant {
    [Util setFullScreenPopUp:nil dismissible:NO animated:YES withBackground:nil];
}

+ (NSString*)_value {
    NSString* curUserID = [STStampedAPI sharedInstance].currentUser.userID;
    return curUserID ? curUserID : @" ";
}

+ (void)present {
    [[NSUserDefaults standardUserDefaults] setObject:[self _value] forKey:_hasShownPopUpUserDefaultsKey];
    STGuidePopUp* popUp = [[[STGuidePopUp alloc] init] autorelease];
    [Util setFullScreenPopUp:popUp dismissible:NO animated:YES withBackground:[UIColor colorWithWhite:0 alpha:.7]];
}

+ (BOOL)shouldShowPopUp {
    NSString* value = [[NSUserDefaults standardUserDefaults] objectForKey:_hasShownPopUpUserDefaultsKey];
    return !value || ![value isEqualToString:[self _value]];
}

- (void)scrollViewDidScroll:(UIScrollView *)scrollView {
}

- (void)scrollViewDidEndDecelerating:(UIScrollView *)scrollView {
    NSInteger page = floor(scrollView.contentOffset.x * 1.0 / scrollView.frame.size.width + .5);
    self.pageControl.currentPage = page;
    [self.pageControl setNeedsDisplay];
}

@end
