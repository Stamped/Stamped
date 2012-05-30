//
//  STPagedImageViewer.h
//  Stamped
//
//  Created by Devin Doty on 5/28/12.
//
//

#import <UIKit/UIKit.h>

@class STPageControl;
@interface STPagedImageViewer : UIView {
    NSInteger _currentPage;
    NSArray *_views;
    BOOL _observing;
}

@property (nonatomic,strong) NSArray *imageURLs;
@property (nonatomic,strong,readonly) UIScrollView *scrollView;
@property (nonatomic,strong,readonly) STPageControl *pageControl;

- (void)moveToPage:(NSInteger)page animated:(BOOL)animated;

@end
