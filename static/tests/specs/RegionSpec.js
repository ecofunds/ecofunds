describe('Region Spec', function() {
    beforeEach(function() {
        this.region = new Region();
    });

    it('Model must have default configs', function() {
        expect(this.region.get('name')).toEqual("Region Name");
        expect(this.region.get('polygons')).toEqual([]);
    });

    it('Must have a visible function', function() {
        expect(this.region.area_visible()).toBe(true);

        this.region.visible(false);

        expect(this.region.area_visible()).toBe(false);
    });
});
